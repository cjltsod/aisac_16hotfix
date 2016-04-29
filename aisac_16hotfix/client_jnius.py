import hashlib
import logging
import os
import traceback

import jnius_config


def md5sum(filename):
    with open(filename, mode='rb') as f:
        d = hashlib.md5()
        d.update(f.read())
    return d.hexdigest()


def gen_client(
        account, pwd,
        clientcert_path=None, clientcert_passphase=None,
        truststore_path=None, truststore_passphase=None,
        java_home=None, class_path=None
):
    try:
        if java_home:
            logging.debug('Setting JAVA_HOME to {}'.format(java_home))
            os.environ['JAVA_HOME'] = java_home
    except:
        logging.warning('Exception when setting JAVA_HOME.')
        logging.warning(traceback.format_exc())

    try:
        if class_path:
            logging.debug(
                'Adding CLASSPATH to {}'.format(
                    ','.join(class_path)
                )
            )
            jnius_config.add_classpath(*class_path)
    except:
        logging.warning('Exception when setting CLASSPATH.')
        logging.warning(traceback.format_exc())

    try:
        from jnius import autoclass
        GisacClient = autoclass('gisac.api.GisacClient')
    except:
        logging.error('Exception when setting autoclass GisacClient.')
        logging.error(traceback.format_exc())
        raise

    try:
        client = GisacClient(
            clientcert_path, clientcert_passphase,
            truststore_path, truststore_passphase,
            account, pwd
        )
    except:
        logging.error('Exception when creating GisacClient object.')
        logging.error(traceback.format_exc())
        raise

    return client


def recieve(client):
    def gen_generator(client, ids):
        ids.insert(0, 'ICST-EWA-201604-0001')
        for each_id in ids:
            exchangeData = client.getIodef(each_id)

            doc = exchangeData.getDoc()
            if doc:
                doc = doc.tostring()

            yield dict(
                id=each_id,
                unitId=exchangeData.getFromUnitId(),
                intelligenceTypeId=exchangeData.getIntelligenceTypeId(),
                iodefTypeId=exchangeData.getIodefTypeId(),
                doc=doc,
            )

    logging.debug('Current client_jnius Version 1604250120.')

    try:
        from jnius import autoclass
        java_ArrayList = autoclass('java.util.ArrayList')
    except:
        logging.error('Exception when autoclass Java built-in types.')
        raise

    jresults = java_ArrayList(client.getUnReadIodefIds())
    results = list()
    for i in range(len(jresults)):
        results.append(jresults[i])

    return gen_generator(client, results)


def send(
        client,
        intelligenceTypeId, iodefTypeId, filepath,
        toUnitIds=2,
):
    logging.debug('Current client_jnius Version 1604250120.')

    try:
        toUnitIds = int(toUnitIds)
        intelligenceTypeId = int(intelligenceTypeId)
        iodefTypeId = int(iodefTypeId)
    except:
        logging.error('Exception when parsing arguments as integer.')
        raise

    logging.debug('toUnitId: {}'.format(toUnitIds))
    logging.debug('intelligenceTypeId: {}'.format(intelligenceTypeId))
    logging.debug('iodefTypeID: {}'.format(iodefTypeId))
    logging.debug('filepath: {}'.format(filepath))

    try:
        from jnius import autoclass
        java_int = autoclass('java.lang.Integer')
        java_ArrayList = autoclass('java.util.ArrayList')
    except:
        logging.error('Exception when autoclass Java built-in types.')
        raise

    try:
        toUnitIds = java_int(toUnitIds)
        intelligenceTypeId = java_int(intelligenceTypeId)
        iodefTypeId = java_int(iodefTypeId)
    except:
        logging.error('Exception when parsing argument as Java integer')
        raise

    try:
        with open(filepath, 'rb') as f:
            doc = f.read()
    except:
        logging.error('Exception when reading iodef.')
        raise

    try:
        checksum = md5sum(filepath)
    except:
        logging.error('Exception when calculating md5sum.')
        raise

    logging.debug('MD5 checksum: {}'.format(checksum))

    try:
        logging.debug('Start sending...')
        results = client.send(
            toUnitIds, intelligenceTypeId, iodefTypeId, doc, checksum
        )
        logging.debug('Complete!')
        logging.debug('Printing Result...')
        results = java_ArrayList(results)
        result_list = list()
        for i in range(len(results)):
            result_list.append(results[i])
            logging.debug('****************************')
            logging.debug(results[i])
    except:
        logging.error('Exception when sending to server.')
        logging.error(traceback.format_exc())

    logging.debug('****************************')
    logging.debug('End of Process.')

    return result_list
