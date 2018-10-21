'''
Identity-Based Proxy Re-Encryption

| From: "M. Green, G. Ateniese Identity-Based Proxy Re-Encryption", Section 4.1.
| Published in: Applied Cryptography and Network Security. Springer Berlin/Heidelberg, 2007
| Available from: http://link.springer.com/chapter/10.1007%2F978-3-540-72738-5_19

* type:           proxy encryption (identity-based)
* setting:        bilinear groups (symmetric)

:Authors:    N. Fotiou
:Date:       7/2016
'''
from charm.toolbox.pairinggroup import pc_element, ZR, G1, G2, GT, pair
from charm.toolbox.hash_module import Hash
from charm.adapters.pkenc_adapt_hybrid import HybridEnc
from charm.core.engine.util import objectToBytes, bytesToObject

debug = False


class PreGA:
    """
	>>>  from charm.toolbox.pairinggroup import PairingGroup,GT
	>>>  from charm.core.engine.util import objectToBytes,bytesToObject
	>>>  from charm.schemes.pkenc.pkenc_cs98 import CS98
	>>>  from charm.toolbox.ecgroup import ECGroup
	>>>  from charm.toolbox.eccurve import prime192v2
	>>>  group = PairingGroup('SS512', secparam=1024)
	>>>  groupcs98 = ECGroup(prime192v2)
	>>>  pkenc = CS98(groupcs98)
	>>>  pre = PreGA(group,pkenc)
	>>>  ID1 = "nikos fotiou"
	>>>  msg  =  group.random(GT)
	>>>  (master_secret_key, params) = pre.setup()
	>>>  (public_key, secret_key) = pkenc.keygen()
	>>>  id1_secret_key = pre.keyGen(master_secret_key, ID1)
	>>>  ciphertext = pre.encrypt(params, ID1, msg);
	>>>  re_encryption_key = pre.rkGenPKenc(params,id1_secret_key, public_key)
	>>>  ciphertext2 = pre.reEncryptPKenc(params, re_encryption_key, ciphertext)
	>>>  pre.decryptPKenc(params,public_key, secret_key, ciphertext2)
    """

    def __init__(self, groupObj, pkencObj=None):
        global group, h, pkenc
        group = groupObj
        h = Hash(group)
        if pkencObj != None:
            pkenc = HybridEnc(pkencObj, msg_len=20)

    def setup(self):
        s = group.random(ZR)
        g = group.random(G1)
        msk = {'s': s}
        params = {'g': g, 'g_s': g ** s}
        if (debug):
            print("Public parameters...")
            group.debug(params)
            print("Master secret key...")
            group.debug(msk)
        return (msk, params)

    def keyGen(self, msk, ID):
        k = group.hash(ID, G1) ** msk['s']
        skid = {'skid': k}
        if (debug):
            print("Key for id => '%s'" % ID)
            group.debug(skid)
        return skid

    def encrypt(self, params, ID, m, skid, t):
        r = h.group.random(ZR)
        C1 = params['g'] ** r
        C2 = m * (pair(params['g_s'], group.hash(ID, G1)) ** (r * h.hashToZr(skid['skid'], t)))
        C3 = t
        ciphertext = {'C1': C1, 'C2': C2, 'C3': C3}
        if debug:
            print('m=>')
            print(m)
            print('ciphertext => ')
            print(ciphertext)
        return ciphertext

    def decrypt(self, params, skid, cid, t):
        if len(cid) == 2:  # first level ciphertext
            m = cid['C2'] / (pair(cid['C1'], skid['skid']) ** h.hashToZr(skid['skid'], t))
        if len(cid) == 4:  # second level ciphertext
            x = self.decrypt(params, skid, {'C1': cid['C3'], 'C2': cid['C4']}, t)
            m = cid['C2'] / pair(cid['C1'], group.hash(x, G1))
        if debug:
            print('\nDecrypting...')
            print('m=>')
            print(m)
        return m

    def rkGen(self, params, skid, ID2, t):
        X = group.random(GT)
        enc = self.encrypt(params, ID2, X, skid, t)

        rk = {'R1': enc['C1'],
              'R2': enc['C2'],
              'R3': (skid['skid'] ** (-h.hashToZr(skid['skid'], t))) * group.hash(X, G1),
              'R4': group.hash(X, G1)}
        if debug:
            print("\nRe-encryption key  =>")
            print(rk)
        return rk

    def reEncrypt(self, params, rk, cid):
        """
        Looks like there is a mistake in the paper, sk_id_i, the proxy has the secret id from id_i?
        """
        ciphertext = {'C1': cid['C1'],
                      'C2': cid['C2'] * pair(cid['C1'],
                                             (rk['R3'] ** (-h.hashToZr(rk['R3'], cid['C3']))) * rk['R4']),
                      'C3': rk['R1'],
                      'C4': rk['R2']}
        if debug:
            print('ciphertext => ')
            print(ciphertext)
        return ciphertext

    def rkGenPKenc(self, params, skid, public_key):
        X = group.random(GT)
        Xbytes = objectToBytes(X, group)
        enc = pkenc.encrypt(public_key, Xbytes)
        rk = {'R1': enc,
              'R2': (1 / (skid['skid'])) * group.hash(X, G1)}
        if (debug):
            print("\nRe-encryption key  =>")
            print(rk)
        return rk

    def reEncryptPKenc(self, params, rk, cid):
        ciphertext = {'C1': cid['C1'], 'C2': cid['C2'] * pair(cid['C1'], rk['R2']), 'C3': rk['R1']}
        if (debug):
            print('ciphertext => ')
            print(ciphertext)
        return ciphertext

    def decryptPKenc(self, params, public_key, secret_key, cid):
        Xbytes = pkenc.decrypt(public_key, secret_key, cid['C3'])
        X = bytesToObject(Xbytes, group)
        m = cid['C2'] / pair(cid['C1'], group.hash(X, G1))
        if (debug):
            print('\nDecrypting...')
            print('m=>')
            print(m)
        return m


if __name__ == '__main__':
    from charm.toolbox.pairinggroup import PairingGroup, GT, extract_key
    from charm.toolbox.symcrypto import SymmetricCryptoAbstraction

    group = PairingGroup('SS512', secparam=1024)
    pre = PreGA(group)
    ID1 = "id_name_1"
    ID2 = "id_name_2"
    msg = b'Message to encrypt'
    type_attribute = group.random(ZR)

    print('Message: {}'.format(msg))

    symcrypto_key = group.random(GT)
    print(symcrypto_key)
    symcrypto = SymmetricCryptoAbstraction(extract_key(symcrypto_key))
    bytest_text = symcrypto.encrypt(msg)

    (master_secret_key, params) = pre.setup()

    # Run by trusted party, someone needs to handle the master secret key
    id1_secret_key = pre.keyGen(master_secret_key, ID1)
    id2_secret_key = pre.keyGen(master_secret_key, ID2)

    # Run by delegator (id_name_1)
    ciphertext = pre.encrypt(params, ID1, symcrypto_key, id1_secret_key, type_attribute)

    print('id1_secret: ')
    print(id1_secret_key)

    # Run by delegator (id_name_1) create reencryption key for ID2, used by the proxy
    re_encryption_key = pre.rkGen(params, id1_secret_key, ID2, type_attribute)

    # Run by the proxy, uses the re encryption key generated by ID1
    ciphertext2 = pre.reEncrypt(params, re_encryption_key, ciphertext)

    # Run by the delegatee (id_name_2)
    symcrypto_key_decrypted = pre.decrypt(params, id2_secret_key, ciphertext2, type_attribute)
    print(symcrypto_key_decrypted)

    symcrypto = SymmetricCryptoAbstraction(extract_key(symcrypto_key_decrypted))
    decrypted_ct = symcrypto.decrypt(bytest_text)

    print('Decrypted: {}'.format(decrypted_ct))

    """
    Master secret key is leading, every user key generated by it is able to decrypt messages from the proxy
    """
