import json
import sqlite3
import logging
import pandas as pd

# Log Yapılandırması
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ERPProcureToPayEngine:
    def __init__(self, data_file='p2p_data.json', db_path='erp_finance.db'):
        self.data_file = data_file
        self.db_path = db_path

    def load_transactions(self):
        with open(self.data_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def validate_approval_matrix(self, po_number, total_amount, approval_level):
        """Harcama limitine göre yetki matrisi kontrolü."""
        if total_amount > 50000 and approval_level != 'CFO':
            logging.error(f"[{po_number}] BÜTÇE İHLALİ: {total_amount} TL tutarındaki işlem için CFO onayı gerekli! Onay Seviyesi: {approval_level}")
            return False
        elif total_amount > 10000 and approval_level not in ['DIRECTOR', 'CFO']:
            logging.error(f"[{po_number}] YETKİ İHLALİ: {total_amount} TL tutarındaki işlem için Direktör onayı gerekli!")
            return False
        return True

    def three_way_match(self, item):
        """3'lü Eşleşme Kontrolü: PO (Sipariş), GR (Mal Kabul) ve Fatura Tutarlılığı."""
        po_qty = item['ordered_qty']
        po_price = item['unit_price']
        gr_qty = item['received_qty']
        inv_qty = item['invoiced_qty']
        inv_price = item['invoiced_price']

        discrepancies = []

        # 1. Fiyat Eşleşmesi Kontrolü
        if inv_price != po_price:
            discrepancies.append(f"Fiyat Uyumsuzluğu: Sipariş Fiyatı={po_price}, Fatura Fiyatı={inv_price}")

        # 2. Miktar Eşleşmesi Kontrolü (Teslim alınan miktardan fazla fatura kesilemez)
        if inv_qty > gr_qty:
            discrepancies.append(f"Miktar Uyumsuzluğu: Teslim Alınan={gr_qty}, Faturaya Kesilen={inv_qty}")

        return len(discrepancies) == 0, discrepancies

    def process_p2p_workflow(self):
        logging.info("ERP Procure-to-Pay (P2P) Süreç Motoru Çalıştırılıyor...")
        transactions = self.load_transactions()
        approved_records = []
        blocked_records = []

        for item in transactions:
            po = item['po_number']
            total_val = item['ordered_qty'] * item['unit_price']
            
            # 1. Onay Matrisi Kontrolü
            is_approved = self.validate_approval_matrix(po, total_val, item['approval_level_required'])
            
            # 2. 3-Way Matching Kontrolü
            match_success, errors = self.three_way_match(item)

            if is_approved and match_success:
                logging.info(f"[{po}] BAŞARILI: 3'lü Eşleşme Sağlandı ve Onaylandı. Fatura ödeme listesine alındı.")
                item['status'] = 'APPROVED_FOR_PAYMENT'
                approved_records.append(item)
            else:
                logging.warning(f"[{po}] BLOKE EDİLDİ! Sebepler: {errors if not match_success else 'Yetki Yetersiz'}")
                item['status'] = 'BLOCKED'
                item['audit_errors'] = str(errors)
                blocked_records.append(item)

        # 3. Veritabanına Aktarım
        self.save_to_database(approved_records, blocked_records)

    def save_to_database(self, approved, blocked):
        conn = sqlite3.connect(self.db_path)
        if approved:
            df_app = pd.DataFrame(approved)
            df_app.to_sql('p2p_approved_payments', conn, if_exists='replace', index=False)
        if blocked:
            df_block = pd.DataFrame(blocked)
            df_block.to_sql('p2p_audit_blocks', conn, if_exists='replace', index=False)
        conn.close()
        logging.info("İşlem sonuçları ERP Finans Veritabanı tablolarına (p2p_approved_payments / p2p_audit_blocks) yazıldı.")

if __name__ == "__main__":
    engine = ERPProcureToPayEngine()
    engine.process_p2p_workflow()
