![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)
![Database](https://img.shields.io/badge/Database-SQLite%20%2F%20SQL-green?style=for-the-badge&logo=sqlite)
![Status](https://img.shields.io/badge/Status-Completed%20PoC-orange?style=for-the-badge)
# ERP Procure-to-Pay (P2P) Workflow & Audit Engine

## Proje Kapsamı ve Kurumsal Mimari
Kurumsal Kaynak Planlama (ERP) sistemlerinde Satın Alma (Procurement) ve Finans (Finance) modüllerinin en kritik kesişim noktası **Procure-to-Pay (P2P)** sürecidir. Bu süreçte yetkisiz harcamaların engellenmesi, bütçe aşımlarının önlenmesi ve sahte/hatalı fatura ödemelerinin önüne geçilmesi için **3'lü Eşleşme (3-Way Matching)** ve **Çok Kademeli Onay Matrisi (Approval Hierarchy)** uygulanır.

Bu proje; kurumsal bir ERP sisteminde gerçekleşen Talep -> Sipariş -> Mal Kabul -> Fatura akışını simüle eden ve iş kuralları ile denetim mekanizmalarını (Audit Trail) çalıştıran bir **ERP İş Mantığı Engine** çalışmasıdır.

### Öne Çıkan ERP Özellikleri
- **Multi-Level Approval Matrix:** Harcama tutarına göre (Örn: <10k $ Kısım Müdürü, >50k $ Direktör/CFO) dinamik onay mekanizması.
- **3-Way Matching Algorithm:** Satın Alma Siparişi (PO), Mal Kabul İrsaliyesi (GR) ve Tedarikçi Faturasının (Invoice) miktar ve fiyat bazında %0 toleransla doğruluk kontrolü.
- **Discrepancy Logging & Fraud Prevention:** Fiyat/miktar uyumsuzluğu olan faturaların otomatik blokelenmesi ve denetim loguna (`p2p_audit.log`) işlenmesi.
- **Automated Ledger Ingestion:** Doğrulanmış işlemlerin Muhasebe/Finans veritabanı şemasına aktarımı.

### Kullanılan Teknolojiler
- **Dil:** Python 3.x
- **Kütüphaneler:** Pandas, JSON, Logging, SQLite
