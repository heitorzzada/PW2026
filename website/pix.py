import binascii
import urllib.parse

def crc16_ccitt(data: str) -> str:
    """Calcula o checksum CRC16-CCITT no padrão Pix (polinômio 0x1021)."""
    crc = 0xFFFF
    for char in data.encode("utf-8"):
        crc ^= char << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = ((crc << 1) ^ 0x1021) & 0xFFFF
            else:
                crc = (crc << 1) & 0xFFFF
    return f"{crc:04X}"


def format_emv_field(field_id: str, value: str) -> str:
    """Formata um campo EMV com seu ID, tamanho (2 dígitos) e conteúdo."""
    length = f"{len(value):02d}"
    return f"{field_id}{length}{value}"


def gerar_payload_pix(chave_pix: str, nome_recebedor: str, cidade_recebedor: str, valor: float, txid: str = "DELACRUZ") -> str:
    """
    Gera a string oficial do Pix Copia-e-Cola (BR Code / EMV).
    """
    # 00: Formato
    payload = format_emv_field("00", "01")
    
    # 26: Informações da conta Pix
    merchant_gui = format_emv_field("00", "br.gov.bcb.pix")
    merchant_key = format_emv_field("01", chave_pix)
    merchant_info = merchant_gui + merchant_key
    payload += format_emv_field("26", merchant_info)
    
    # 52: Merchant Category Code
    payload += format_emv_field("52", "0000")
    
    # 53: Moeda (986 = BRL)
    payload += format_emv_field("53", "986")
    
    # 54: Valor (opcional ou fixo)
    if valor and valor > 0:
        payload += format_emv_field("54", f"{valor:.2f}")
    
    # 58: País
    payload += format_emv_field("58", "BR")
    
    # 59: Nome do Recebedor (max 25 chars)
    nome = nome_recebedor[:25]
    payload += format_emv_field("59", nome)
    
    # 60: Cidade (max 15 chars)
    cidade = cidade_recebedor[:15]
    payload += format_emv_field("60", cidade)
    
    # 62: Dados adicionais (TxID)
    ref_label = format_emv_field("05", txid[:25])
    payload += format_emv_field("62", ref_label)
    
    # 63: CRC16 prefix
    payload_to_hash = payload + "6304"
    crc = crc16_ccitt(payload_to_hash)
    
    return payload_to_hash + crc


def gerar_url_qrcode_pix(payload_pix: str, tamanho: int = 250) -> str:
    """
    Retorna a URL para gerar o QR Code diretamente via serviço de renderização pública.
    """
    encoded_payload = urllib.parse.quote(payload_pix)
    return f"https://api.qrserver.com/v1/create-qr-code/?size={tamanho}x{tamanho}&data={encoded_payload}"
