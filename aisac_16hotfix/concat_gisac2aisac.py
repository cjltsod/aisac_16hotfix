import hashlib
import json

from aisac_16hotfix import client_jnius


def cal_md5(s):
    m = hashlib.md5()
    try:
        m.update(s.encode())
    except:
        m.update(s)
    return m.hexdigest()


def aisac_submit(user_name, user_pass, data_string, iodef_type_id):
    try:
        import requests
        from requests.auth import HTTPBasicAuth
    except:
        raise Exception('Requests is not installed. Run installation first.')

    SERVER = 'https://test.aisac.tw/v0.1/iodef/'
    md5_value = cal_md5(data_string)
    data = {
        'iodef_type_id': iodef_type_id,
        'iodef': data_string,
        'iodef_md5_value': md5_value,
    }
    r = requests.post(SERVER, data=data, auth=HTTPBasicAuth(user_name, user_pass))
    return r.text


ERROR_IODEF_IDS = list()


def concat_gisac2aisac(iodef_obj, config=None, **kwargs):
    aisac_username = config['AISAC']['username']
    aisac_userpass = config['AISAC']['password']

    iodef_type_id = iodef_obj.getIodefTypeId()
    raw_data = bytes(iodef_obj.doc.tolist())
    data_string = raw_data.decode('utf-8')

    submit_result_text = aisac_submit(
        aisac_username, aisac_userpass,
        data_string, iodef_type_id,
    )
    submit_result = json.loads(submit_result_text)
    if submit_result['success']:
        print(submit_result)
        ERROR_IODEF_IDS.remove(iodef_obj.id)
    else:
        print(submit_result)

def handle_before_contact(ids, month_after=None, **kwargs):
    ERROR_IODEF_IDS.extend(ids)

    for each_id in ids:
        id_split = each_id.split('-')
        if len(id_split) == 4:
            if int(id_split[2][:6]) < month_after:
                ids.remove(each_id)

def gisac_receive(
        config,
        client=None,
        ids=None,
        iodef_ids_callback=handle_before_contact,
        each_iodef_callback=concat_gisac2aisac,
        **kwargs
):
    jnius_extrakwargs = {
        'account': config['GISAC']['account'],
        'pwd': config['GISAC']['pwd'],
        'clientcert_path': config['GISAC']['clientcert_path'],
        'clientcert_passphase': config['GISAC']['clientcert_passphase'],
        'truststore_path': config['GISAC']['truststore_path'],
        'truststore_passphase': config['GISAC']['truststore_passphase'],
        'java_home': config['JAVA']['java_home'],
        'class_path': config['JAVA']['class_path'].split(':'),
    }

    if client is None:
        client = client_jnius.gen_client(**jnius_extrakwargs)
    if not ids:
        ids = client.getUnReadIodefIds().toArray()
    else:
        ids = ids.copy()

    iodef_ids_callback(ids, **kwargs)

    for each_id in ids:
        iodef = client.getIodef(each_id)
        each_iodef_callback(iodef, config=config, **kwargs)

    return client


def main(config=None, cfg_file_path=None):
    if not config:
        from aisac_16hotfix import handle_config
        config = handle_config(cfg_file_path)

    try:
        with open('error_iodef_ids.txt', 'r') as infile:
            ERROR_IODEF_IDS.extend(json.loads(infile.read()))
    except:
        print('Unable to retrieve last error list.')

    java_client = None
    if ERROR_IODEF_IDS:
        print('Handling last error list...')
        java_client = gisac_receive(java_client=java_client, config=config, ids=ERROR_IODEF_IDS, month_after=201705)
    print('Handling new iodefs')
    java_client = gisac_receive(client=java_client, config=config, ids=['MJIB-DEF-201509-0001'], month_after=201705)

    with open('error_iodef_ids.txt', 'w') as outfile:
        output_sets = set(ERROR_IODEF_IDS)
        output_list = list(output_sets)
        json.dump(output_list, outfile)


if __name__ == "__main__":
    main()
