from http import HTTPStatus
from urllib.parse import urlencode, unquote

import requests
from django.shortcuts import render
from django.views import View

from utils import get_client_ip
from .crypto import encrypt_to_base64, decrypt_from_base64
from .forms import PhoneNumberRequestForm
from .models import PhoneNumberRequestLog


class PhoneNumberView(View):
    url = 'http://section.cgv.co.kr/ajax/ticket/GetMobileNumber.aspx'
    proxy_url = 'http://ticket.cgv.co.kr/CGV2011/RIA/RR000.aspx/CJ_VW_HTTPCONTEXT'
    headers = {
        'Referer': 'http://ticket.cgv.co.kr/Reservation/Reservation.aspx',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0'
    }
    timeout = 30

    template_name = 'cgv/id2pn.html'

    def get(self, request, *args, **kwargs):
        context = {}
        if not request.GET:
            context['form'] = PhoneNumberRequestForm()
            return render(request, self.template_name, context)

        form = PhoneNumberRequestForm(request.GET)
        context['form'] = form
        if not form.is_valid():
            return render(request, self.template_name, context, status=HTTPStatus.BAD_REQUEST)

        user_id = form.cleaned_data['user_id']
        fields = {
            'ip': get_client_ip(request),
            'user_id': user_id,
        }

        params = urlencode({'userId': encrypt_to_base64(user_id)})
        url = f'{self.url}?{params}'
        enc_params = {'strURL': encrypt_to_base64(url)}
        try:
            res = requests.post(self.proxy_url, json=enc_params, headers=self.headers, timeout=self.timeout)
            fields['status_code'] = str(res.status_code)
            fields['raw_response'] = res.text
            res.raise_for_status()

            content = res.json()
            data = content['d']['data']['DATA']
            data = unquote(data)

            if not data.startswith('00000') or len(data) < 9:
                raise ValueError('No such user ID or phone number')

            phone_number = decrypt_from_base64(data[9:])
            fields['phone_number'] = phone_number

            status = HTTPStatus.OK
            msg = phone_number
        except requests.Timeout:
            msg = 'Request timed out'
            status = HTTPStatus.REQUEST_TIMEOUT
            fields['error_msg'] = msg
        except requests.HTTPError:
            msg = 'HTTP error occured'
            status = HTTPStatus.BAD_REQUEST
            fields['error_msg'] = msg
        except KeyError:
            msg = 'Unknown response format'
            status = HTTPStatus.BAD_REQUEST
            fields['error_msg'] = msg
        except ValueError as e:
            msg = str(e)
            status = HTTPStatus.NOT_FOUND
            fields['error_msg'] = msg

        instance = PhoneNumberRequestLog(**fields)
        instance.full_clean()
        instance.save()

        context['success'] = status is HTTPStatus.OK
        context['msg'] = msg

        return render(request, self.template_name, context, status=status)
