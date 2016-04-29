import configparser
import datetime
import psutil
import logging
import os

from . import client_jnius, client_suds, db


def handle_config(cfg_file_path):
    if not cfg_file_path:
        cfg_file_path = '{}/aisac_16hotfix.cfg'.format(os.getcwd())

    config = configparser.ConfigParser()
    print('Parsing config \'{}\'...'.format(cfg_file_path))

    try:
        config.read(cfg_file_path)
        print('Parsing config \'{}\'...Done'.format(cfg_file_path))
    except:
        print('Config file not found, regenerating...')

    cwd = os.getcwd()

    if '16HOTFIX' not in config.sections():
        config['16HOTFIX'] = {}
    if 'GISAC' not in config.sections():
        config['GISAC'] = {}
    if 'JAVA' not in config.sections():
        config['JAVA'] = {}
    if 'SSH' not in config.sections():
        config['SSH'] = {}

    if 'db_connect_string' not in config['16HOTFIX'].keys():
        config['16HOTFIX']['db_connect_string'] = \
            'mysql://account:password@host/database?charset=utf8'
    if 'db_result_write_back' not in config['16HOTFIX'].keys():
        config['16HOTFIX']['db_result_write_back'] = 'False'
    if 'logging_level' not in config['16HOTFIX']:
        config['16HOTFIX']['logging_level'] = 'INFO'
    if config['16HOTFIX']['logging_level'] not in logging._nameToLevel.keys():
        config['16HOTFIX']['logging_level'] = 'INFO'
    if 'logging_date_fmt' not in config['16HOTFIX'].keys():
        config['16HOTFIX']['logging_date_fmt'] = '%%m/%%d/%%Y %%I:%%M:%%S %%p'
    if 'logging_file_fmt' not in config['16HOTFIX'].keys():
        config['16HOTFIX']['logging_file_fmt'] = \
            '{}/log/%%Y-%%m-%%d.log'.format(cwd)
    if 'logging_fmt' not in config['16HOTFIX'].keys():
        config['16HOTFIX']['logging_fmt'] = \
            '%%(asctime)s [%%(threadName)-12.12s][%%(levelname)-5.5s]' \
            ' %%(message)s'
    if 'pid_file' not in config['16HOTFIX'].keys():
        config['16HOTFIX']['pid_file'] = '{}/16hotfix.pid'.format(cwd)
    if 'timeout' not in config['16HOTFIX'].keys():
        config['16HOTFIX']['timeout'] = '3600'

    if 'account' not in config['GISAC'].keys():
        config['GISAC']['account'] = 'AISAC'
    if 'pwd' not in config['GISAC'].keys():
        config['GISAC']['pwd'] = 'REAL_PASSWORD_HERE'
    if 'clientcert_path' not in config['GISAC'].keys():
        config['GISAC']['clientcert_path'] = '{}/clientcert.jks'.format(cwd)
    if 'clientcert_passphase' not in config['GISAC'].keys():
        config['GISAC']['clientcert_passphase'] = 'PASSPHASE_HERE'
    if 'truststore_path' not in config['GISAC'].keys():
        config['GISAC']['truststore_path'] = '{}/trustStore.jks'.format(cwd)
    if 'truststore_passphase' not in config['GISAC'].keys():
        config['GISAC']['truststore_passphase'] = 'PASSPHASE_HERE'

    if 'java_home' not in config['JAVA'].keys():
        config['JAVA']['java_home'] = os.environ.get('JAVAHOME', '')
    if 'class_path' not in config['JAVA'].keys():
        config['JAVA']['class_path'] = os.environ.get(
            'CLASSPATH',
            ':'.join(['.', '{}/lib/*'.format(cwd)]),
        )

    if 'server' not in config['SSH'].keys():
        config['SSH']['server'] = '140.117.101.15'
    if 'port' not in config['SSH'].keys():
        config['SSH']['PORT'] = '22'
    if 'username' not in config['SSH'].keys():
        config['SSH']['username'] = 'root'
    if 'password' not in config['SSH'].keys():
        config['SSH']['password'] = 'SSH_PASSWORD_HERE'
    if 'file_locate' not in config['SSH']:
        config['SSH']['file_locate'] = '/etc/iodef/{}/{}.xml'

    try:
        with open(cfg_file_path, 'w') as f:
            config.write(f)
    except:
        print('Unable to write config to file \'{}\''.format(cfg_file_path))

    return config


def main(cfg_file_path):
    config = handle_config(cfg_file_path)

    logFormatter = logging.Formatter(
        config['16HOTFIX']['logging_fmt'],
        datefmt=config['16HOTFIX']['logging_date_fmt'],
    )
    rootLogger = logging.getLogger()
    rootLogger.setLevel(
        logging._nameToLevel.get(
            config['16HOTFIX']['logging_level'],
            logging.INFO,
        )
    )
    fileHandler = logging.FileHandler(
        datetime.datetime.now().strftime(config['16HOTFIX']['logging_file_fmt'])
    )
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    logging.info('Loading PID file...')
    pid = None
    try:
        with open(config['16HOTFIX']['pid_file'], 'r') as f:
            pid = int(f.read())
    except Exception as e:
        logging.info('No PID file found.')

    if pid:
        if psutil.pid_exists(pid):
            logging.warning('There\'s another instance running... PID({}).'.format(pid))
            proc = psutil.Process(pid)
            delta = datetime.datetime.now() - datetime.datetime.fromtimestamp(proc.create_time())
            if delta > datetime.timedelta(seconds=int(config['16HOTFIX']['timeout'])):
                logging.warning('Terminating... PID({}).'.format(pid))
                proc.terminate()
                gone, alive = psutil.wait_procs([proc], timeout=10)
                for p in alive:
                    logging.warning('Still alive. Killing... PID({}).'.format(pid))
                    p.kill()
            else:
                logging.warning('Target process PID({}) not timeout, terminate myself.'.format(pid))
                return

    with open(config['16HOTFIX']['pid_file'], 'w') as f:
        f.write(str(os.getpid()))

    logging.info('Connecting to database...')
    try:
        from .iodef import get_iodef, save

        engine = db.generate_engine(config['16HOTFIX']['db_connect_string'])
        Base, metadata = db.generate_automap_base_with_metadata(engine)
        announce2GISAC = db.generate_table_announce2GISAC(Base)
        session = db.generate_session(engine)
    except Exception as e:
        logging.exception('Unable to connect to database.')
        raise

    logging.info('Query database...')
    try:
        rows = session.query(announce2GISAC).filter(
            announce2GISAC.responseID == '0',
        ).all()
    except Exception as e:
        logging.exception('Unable to query database.')
        raise

    if rows:
        logging.info(
            'Data for sending found in database...({})'.format(len(rows))
        )
        file_name_list = list()
        for each_row in rows:
            file_name_list.append(each_row.publishID)

        logging.info('Retrieveing iodef files...')
        try:
            file_data_dict = get_iodef(
                file_name_list,
                server=config['SSH']['server'], port=config['SSH']['port'],
                username=config['SSH']['username'],
                password=config['SSH']['password'],
                file_locate=config['SSH']['file_locate'],
            )
        except Exception as e:
            logging.exception('Unable to retrieve iodef files.')
            raise

        logging.info('Writing iodef to local tmp...')
        try:
            for each_filename in file_data_dict.keys():
                save(
                    '/tmp/{}.xml'.format(each_filename),
                    file_data_dict[each_filename],
                )
        except Exception as e:
            logging.exception('Unable to connect to database.')
            raise

        logging.info('Generating GISAC Client...')

        try:
            jnius_extrakwargs = {
                'account': config['GISAC']['account'],
                'pwd': config['GISAC']['pwd'],
                'clientcert_path': config['GISAC']['clientcert_path'],
                'clientcert_passphase':
                    config['GISAC']['clientcert_passphase'],
                'truststore_path': config['GISAC']['truststore_path'],
                'truststore_passphase':
                    config['GISAC']['truststore_passphase'],
                'java_home': config['JAVA']['java_home'],
                'class_path': config['JAVA']['class_path'].split(':'),
            }
        except Exception as e:
            logging.exception('Unable to genereate jnius_extrakwargs.')
            raise

        try:
            client = client_jnius.gen_client(**jnius_extrakwargs)
        except Exception as e:
            logging.exception('Unable to generate client_jnius.')
            raise

        logging.info('Senging iodef...')
        result_dict = dict()
        for each_row in rows:
            try:
                iodefTypeId = each_row.typeId
                intelligenceTypeId = each_row.type
                toUnitIds = each_row.toUnitId
                file_name = each_row.publishID
                file_path = '/tmp/{}.xml'.format(file_name)
                result = client_jnius.send(
                    client=client,
                    filepath=file_path, toUnitIds=toUnitIds,
                    intelligenceTypeId=intelligenceTypeId,
                    iodefTypeId=iodefTypeId,
                )

                logging.info(
                    '{} sent with return result: {}'.format(file_name, result)
                )

                result_dict[file_name] = result

                try:
                    if config['16HOTFIX'].getboolean(
                            'db_result_write_back',
                            fallback=False,
                    ):
                        each_row.responseNumber = result[0]
                        each_row.responseID = result[1]
                        session.commit()
                        logging.info(
                            '{} write back result success.'.format(file_name)
                        )
                except Exception as e:
                    logging.exception('Unable to writeback to database.')
                    raise
            except Exception as e:
                logging.exception('Unable to handle one of row.')
                raise

        if not config['16HOTFIX'].getboolean(
                'db_result_write_back',
                fallback=False,
        ):
            logging.info('Not writing back to database...')
            try:
                session.rollback()
            except Exception as e:
                logging.exception('Unable to rollback databae.')
                raise
    else:
        logging.info('No data required for sending.')

    logging.info('Removing pid file...')
    os.remove(config['16HOTFIX']['pid_file'])
