import logging

from paramiko.client import SSHClient
from paramiko.client import AutoAddPolicy


def get_iodef(
        iodef_name_list,
        server='140.117.101.15',
        port=22, username='root',
        password=None,
        file_locate='/etc/iodef/{}/{}.xml'
):
    logging.debug('Generating ssh client...')
    client = SSHClient()
    logging.debug('Loading system host key...')
    client.load_system_host_keys()

    # disable following if known_hosts
    logging.debug('Setting missing host key policy to AutoAddPolicy...')
    client.set_missing_host_key_policy(AutoAddPolicy())

    logging.debug('Connecting to ssh {}@{}:{}...'.format(
        username, server, port,
    ))
    client.connect(
        server, port=port, username=username, password=password,
        timeout=5,
    )

    logging.debug('Generating sftp...')
    sftp_client = client.open_sftp()

    return_dict = dict()
    for each_iodef_name in iodef_name_list:
        try:
            quote = '/'.join(each_iodef_name.split('-')[:-1])
            file_path = file_locate.format(quote, each_iodef_name)

            logging.debug('Touching remote file {}'.format(file_path))
            with sftp_client.open(file_path) as f:
                logging.debug('Loading remote file {}'.format(file_path))
                return_dict[each_iodef_name] = f.read()
        except Exception as e:
            logging.exception('Unable to retrieve {}'.format(each_iodef_name))

    return return_dict


def save(filepath, byte_data):
    logging.debug('Touching local file {}'.format(filepath))
    with open(filepath, 'wb') as f:
        logging.debug('Writing local file {}'.format(filepath))
        r = f.write(byte_data)
    return r
