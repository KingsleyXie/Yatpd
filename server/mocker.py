import copy


# Common function to mock server/proxy dispatchers
def mock_request(payloads, instance):
    default_params = ['GET', '/', '', b'', {}]

    for rtype in payloads:
        for args in payloads[rtype]:
            params = copy.copy(default_params)
            params[:len(args)] = args

            print(f'Mocking Request With Parameters: {params}')

            res = instance.dispatch(*params)
            res = res if rtype == 'raw' else instance.decode(res)

            print(f'Dispatcher Returned {rtype.upper()} Response:')
            print(f'{"*" * 80}\n{res}\n')
