import crcmod
import qrcode  # Mantemos a importação caso queira usar o QR Code depois
import os

class Payload():
    def __init__(self, nome, chavepix, valor, cidade, txtId, diretorio=''):
        self.nome = nome
        self.chavepix = chavepix
        self.valor = valor.replace(',', '.')
        self.cidade = cidade
        self.txtId = txtId
        self.diretorioQrCode = diretorio

    def _formata_campo(self, id, valor):
        """Auxiliar para garantir que o tamanho tenha sempre 2 dígitos"""
        return f"{id}{len(valor):02}{valor}"

    def gerarPayload(self, gerar_qrcode=False):
        # 00: Payload Format Indicator (Fixo: 01)
        payload_format = self._formata_campo('00', '01')

        # 26: Merchant Account Information
        # Sub-campos do ID 26
        gui = self._formata_campo('00', 'br.gov.bcb.pix')
        chave = self._formata_campo('01', self.chavepix)
        merchant_account = self._formata_campo('26', f"{gui}{chave}")

        # 52: Merchant Category Code (Fixo: 0000)
        mcc = '52040000'

        # 53: Transaction Currency (Fixo: 986 para Real)
        currency = '5303986'

        # 54: Transaction Amount (Formatação com 2 casas decimais)
        valor_str = f"{float(self.valor):.2f}"
        amount = self._formata_campo('54', valor_str)

        # 58: Country Code (Fixo: BR)
        country = '5802BR'

        # 59: Merchant Name
        name = self._formata_campo('59', self.nome)

        # 60: Merchant City
        city = self._formata_campo('60', self.cidade)

        # 62: Additional Data Field (TXID)
        txid = self._formata_campo('05', self.txtId)
        additional_data = self._formata_campo('62', txid)

        # Montagem parcial para cálculo do CRC16
        self.payload_sem_crc = (
            f"{payload_format}{merchant_account}{mcc}{currency}"
            f"{amount}{country}{name}{city}{additional_data}6304"
        )

        # Cálculo do CRC16
        self.gerarCrc16(self.payload_sem_crc)

        if gerar_qrcode:
            self.gerarQrCode(self.payload_completa, self.diretorioQrCode)

        return self.payload_completa

    def gerarCrc16(self, payload):
        crc16_func = crcmod.mkCrcFun(poly=0x11021, initCrc=0xFFFF, rev=False, xorOut=0x0000)
        crc_hex = hex(crc16_func(payload.encode('utf-8')))
        self.crc16Code_formatado = str(crc_hex).replace('0x', '').upper().zfill(4)
        self.payload_completa = f"{payload}{self.crc16Code_formatado}"

    def gerarQrCode(self, payload, diretorio):
        dir_path = os.path.expanduser(diretorio)
        if not os.path.exists(dir_path) and dir_path != '':
            os.makedirs(dir_path)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(payload)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img.save(os.path.join(dir_path, 'pix_qrcode.png'))