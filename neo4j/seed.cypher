// Idempotent Inventory Knowledge Graph Seed Script
// 1. Create Sites
MERGE (s1:Site {site_code: 'S01'}) SET s1.name = 'Headquarters', s1.city = 'New York', s1.country = 'USA', s1.timezone = 'EST';
MERGE (s2:Site {site_code: 'S02'}) SET s2.name = 'West Coast Warehouse', s2.city = 'Los Angeles', s2.country = 'USA', s2.timezone = 'PST';
MERGE (s3:Site {site_code: 'S03'}) SET s3.name = 'European Hub', s3.city = 'Berlin', s3.country = 'Germany', s3.timezone = 'CET';

// 2. Create Locations
MERGE (l1:Location {location_code: 'HQ-FL1'}) SET l1.name = 'Floor 1 Storage';
MERGE (l2:Location {location_code: 'HQ-IT'}) SET l2.name = 'IT Department';
MERGE (l3:Location {location_code: 'WC-A1'}) SET l3.name = 'Aisle 1 Storage';
MERGE (l4:Location {location_code: 'WC-A2'}) SET l4.name = 'Aisle 2 High-Bay';
MERGE (l5:Location {location_code: 'EU-MAIN'}) SET l5.name = 'Main Storage';

// Link Locations to Sites
MATCH (l1:Location {location_code: 'HQ-FL1'}), (s1:Site {site_code: 'S01'}) MERGE (l1)-[:BELONGS_TO]->(s1);
MATCH (l2:Location {location_code: 'HQ-IT'}), (s1:Site {site_code: 'S01'}) MERGE (l2)-[:BELONGS_TO]->(s1);
MATCH (l3:Location {location_code: 'WC-A1'}), (s2:Site {site_code: 'S02'}) MERGE (l3)-[:BELONGS_TO]->(s2);
MATCH (l4:Location {location_code: 'WC-A2'}), (s2:Site {site_code: 'S02'}) MERGE (l4)-[:BELONGS_TO]->(s2);
MATCH (l5:Location {location_code: 'EU-MAIN'}), (s3:Site {site_code: 'S03'}) MERGE (l5)-[:BELONGS_TO]->(s3);

// 3. Create Categories
MERGE (cat1:Category {name: 'Electronics'});
MERGE (cat2:Category {name: 'Furniture'});
MERGE (cat3:Category {name: 'Networking'});
MERGE (cat4:Category {name: 'Accessories'});

// 4. Create Items
MERGE (i1:Item {item_code: 'ITM-001'}) SET i1.name = 'ThinkPad T14 Laptop', i1.unit_of_measure = 'EA';
MERGE (i2:Item {item_code: 'ITM-002'}) SET i2.name = 'Ergonomic Office Chair', i2.unit_of_measure = 'EA';
MERGE (i3:Item {item_code: 'ITM-003'}) SET i3.name = 'Wireless Ergonomic Mouse', i3.unit_of_measure = 'EA';
MERGE (i4:Item {item_code: 'ITM-004'}) SET i4.name = 'Cisco Gigabit Switch 24-Port', i4.unit_of_measure = 'EA';
MERGE (i5:Item {item_code: 'ITM-005'}) SET i5.name = 'Dell UltraSharp 27 Monitor', i5.unit_of_measure = 'EA';
MERGE (i6:Item {item_code: 'ITM-006'}) SET i6.name = 'MacBook Pro 16 M3', i6.unit_of_measure = 'EA';

// Link Items to Categories
MATCH (i1:Item {item_code: 'ITM-001'}), (cat1:Category {name: 'Electronics'}) MERGE (i1)-[:IN_CATEGORY]->(cat1);
MATCH (i2:Item {item_code: 'ITM-002'}), (cat2:Category {name: 'Furniture'}) MERGE (i2)-[:IN_CATEGORY]->(cat2);
MATCH (i3:Item {item_code: 'ITM-003'}), (cat4:Category {name: 'Accessories'}) MERGE (i3)-[:IN_CATEGORY]->(cat4);
MATCH (i4:Item {item_code: 'ITM-004'}), (cat3:Category {name: 'Networking'}) MERGE (i4)-[:IN_CATEGORY]->(cat3);
MATCH (i5:Item {item_code: 'ITM-005'}), (cat1:Category {name: 'Electronics'}) MERGE (i5)-[:IN_CATEGORY]->(cat1);
MATCH (i6:Item {item_code: 'ITM-006'}), (cat1:Category {name: 'Electronics'}) MERGE (i6)-[:IN_CATEGORY]->(cat1);

// 5. Create Vendors
MERGE (v1:Vendor {vendor_code: 'V001'}) SET v1.name = 'Acme Corp', v1.email = 'contact@acme.com', v1.phone = '555-0100', v1.city = 'New York', v1.country = 'USA';
MERGE (v2:Vendor {vendor_code: 'V002'}) SET v2.name = 'TechSupply Inc', v2.email = 'sales@techsupply.com', v2.phone = '555-0101', v2.city = 'San Jose', v2.country = 'USA';
MERGE (v3:Vendor {vendor_code: 'V003'}) SET v3.name = 'Global Office Needs', v3.email = 'hello@globaloffice.com', v3.phone = '555-0102', v3.city = 'London', v3.country = 'UK';
MERGE (v4:Vendor {vendor_code: 'V004'}) SET v4.name = 'Apex Hardware Co', v4.email = 'orders@apex.com', v4.phone = '555-0199', v4.city = 'Chicago', v4.country = 'USA';

// Link Vendors to Items they supply
MATCH (v2:Vendor {vendor_code: 'V002'}), (i1:Item {item_code: 'ITM-001'}) MERGE (v2)-[:SUPPLIES]->(i1);
MATCH (v2:Vendor {vendor_code: 'V002'}), (i5:Item {item_code: 'ITM-005'}) MERGE (v2)-[:SUPPLIES]->(i5);
MATCH (v2:Vendor {vendor_code: 'V002'}), (i6:Item {item_code: 'ITM-006'}) MERGE (v2)-[:SUPPLIES]->(i6);
MATCH (v1:Vendor {vendor_code: 'V001'}), (i3:Item {item_code: 'ITM-003'}) MERGE (v1)-[:SUPPLIES]->(i3);
MATCH (v1:Vendor {vendor_code: 'V001'}), (i4:Item {item_code: 'ITM-004'}) MERGE (v1)-[:SUPPLIES]->(i4);
MATCH (v3:Vendor {vendor_code: 'V003'}), (i2:Item {item_code: 'ITM-002'}) MERGE (v3)-[:SUPPLIES]->(i2);
MATCH (v4:Vendor {vendor_code: 'V004'}), (i4:Item {item_code: 'ITM-004'}) MERGE (v4)-[:SUPPLIES]->(i4);

// 6. Create Assets
MERGE (a1:Asset {asset_tag: 'TAG-1001'}) SET a1.name = 'Lenovo ThinkPad T14 - Gen1', a1.cost = 1200.0, a1.status = 'Active', a1.serial_number = 'SN123456', a1.purchase_date = '2025-01-15';
MERGE (a2:Asset {asset_tag: 'TAG-1002'}) SET a2.name = 'Lenovo ThinkPad T14 - Gen2', a2.cost = 1250.0, a2.status = 'In Repair', a2.serial_number = 'SN123457', a2.purchase_date = '2025-02-01';
MERGE (a3:Asset {asset_tag: 'TAG-1003'}) SET a3.name = 'Herman Miller Chair', a3.cost = 800.0, a3.status = 'Active', a3.serial_number = 'SN998877', a3.purchase_date = '2024-11-20';
MERGE (a4:Asset {asset_tag: 'TAG-1004'}) SET a4.name = 'Dell Monitor 27"', a4.cost = 300.0, a4.status = 'Active', a4.serial_number = 'SN554433', a4.purchase_date = '2025-03-01';
MERGE (a5:Asset {asset_tag: 'TAG-1005'}) SET a5.name = 'Cisco Switch Core', a5.cost = 1500.0, a5.status = 'Active', a5.serial_number = 'SN112233', a5.purchase_date = '2024-06-10';
MERGE (a6:Asset {asset_tag: 'TAG-1006'}) SET a6.name = 'MacBook Pro 16 M3 Max', a6.cost = 2499.0, a6.status = 'Active', a6.serial_number = 'SN889900', a6.purchase_date = '2025-04-01';

// Link Assets to Items, Vendors, and Locations
MATCH (a1:Asset {asset_tag: 'TAG-1001'}), (i1:Item {item_code: 'ITM-001'}) MERGE (a1)-[:INSTANCE_OF]->(i1);
MATCH (a1:Asset {asset_tag: 'TAG-1001'}), (v2:Vendor {vendor_code: 'V002'}) MERGE (a1)-[:PURCHASED_FROM]->(v2);
MATCH (a1:Asset {asset_tag: 'TAG-1001'}), (l2:Location {location_code: 'HQ-IT'}) MERGE (a1)-[:LOCATED_AT]->(l2);

MATCH (a2:Asset {asset_tag: 'TAG-1002'}), (i1:Item {item_code: 'ITM-001'}) MERGE (a2)-[:INSTANCE_OF]->(i1);
MATCH (a2:Asset {asset_tag: 'TAG-1002'}), (v2:Vendor {vendor_code: 'V002'}) MERGE (a2)-[:PURCHASED_FROM]->(v2);
MATCH (a2:Asset {asset_tag: 'TAG-1002'}), (l2:Location {location_code: 'HQ-IT'}) MERGE (a2)-[:LOCATED_AT]->(l2);

MATCH (a3:Asset {asset_tag: 'TAG-1003'}), (i2:Item {item_code: 'ITM-002'}) MERGE (a3)-[:INSTANCE_OF]->(i2);
MATCH (a3:Asset {asset_tag: 'TAG-1003'}), (v3:Vendor {vendor_code: 'V003'}) MERGE (a3)-[:PURCHASED_FROM]->(v3);
MATCH (a3:Asset {asset_tag: 'TAG-1003'}), (l1:Location {location_code: 'HQ-FL1'}) MERGE (a3)-[:LOCATED_AT]->(l1);

MATCH (a4:Asset {asset_tag: 'TAG-1004'}), (i5:Item {item_code: 'ITM-005'}) MERGE (a4)-[:INSTANCE_OF]->(i5);
MATCH (a4:Asset {asset_tag: 'TAG-1004'}), (v2:Vendor {vendor_code: 'V002'}) MERGE (a4)-[:PURCHASED_FROM]->(v2);
MATCH (a4:Asset {asset_tag: 'TAG-1004'}), (l3:Location {location_code: 'WC-A1'}) MERGE (a4)-[:LOCATED_AT]->(l3);

MATCH (a5:Asset {asset_tag: 'TAG-1005'}), (i4:Item {item_code: 'ITM-004'}) MERGE (a5)-[:INSTANCE_OF]->(i4);
MATCH (a5:Asset {asset_tag: 'TAG-1005'}), (v1:Vendor {vendor_code: 'V001'}) MERGE (a5)-[:PURCHASED_FROM]->(v1);
MATCH (a5:Asset {asset_tag: 'TAG-1005'}), (l5:Location {location_code: 'EU-MAIN'}) MERGE (a5)-[:LOCATED_AT]->(l5);

MATCH (a6:Asset {asset_tag: 'TAG-1006'}), (i6:Item {item_code: 'ITM-006'}) MERGE (a6)-[:INSTANCE_OF]->(i6);
MATCH (a6:Asset {asset_tag: 'TAG-1006'}), (v2:Vendor {vendor_code: 'V002'}) MERGE (a6)-[:PURCHASED_FROM]->(v2);
MATCH (a6:Asset {asset_tag: 'TAG-1006'}), (l2:Location {location_code: 'HQ-IT'}) MERGE (a6)-[:LOCATED_AT]->(l2);

// 7. Create Customers
MERGE (c1:Customer {customer_code: 'C001'}) SET c1.name = 'Beta Industries', c1.email = 'billing@beta.com', c1.city = 'Chicago';
MERGE (c2:Customer {customer_code: 'C002'}) SET c2.name = 'Omega Services', c2.email = 'accounts@omega.com', c2.city = 'Austin';

// 8. Create Purchase Orders
MERGE (po1:PurchaseOrder {po_number: 'PO-10001'}) SET po1.order_date = '2025-01-05', po1.status = 'Closed', po1.total_amount = 12000.0;
MERGE (po2:PurchaseOrder {po_number: 'PO-10002'}) SET po2.order_date = '2025-02-01', po2.status = 'Open', po2.total_amount = 4500.0;

MATCH (v2:Vendor {vendor_code: 'V002'}), (po1:PurchaseOrder {po_number: 'PO-10001'}) MERGE (v2)-[:RECEIVED]->(po1);
MATCH (po1:PurchaseOrder {po_number: 'PO-10001'}), (i1:Item {item_code: 'ITM-001'}) MERGE (po1)-[:CONTAINS {quantity: 10, unit_price: 1200.0}]->(i1);

MATCH (v3:Vendor {vendor_code: 'V003'}), (po2:PurchaseOrder {po_number: 'PO-10002'}) MERGE (v3)-[:RECEIVED]->(po2);
MATCH (po2:PurchaseOrder {po_number: 'PO-10002'}), (i2:Item {item_code: 'ITM-002'}) MERGE (po2)-[:CONTAINS {quantity: 5, unit_price: 900.0}]->(i2);

// 9. Create Sales Orders
MERGE (so1:SalesOrder {so_number: 'SO-50001'}) SET so1.order_date = '2025-02-10', so1.status = 'Shipped', so1.total_amount = 3000.0;
MERGE (so2:SalesOrder {so_number: 'SO-50002'}) SET so2.order_date = '2025-03-01', so2.status = 'Processing', so2.total_amount = 1800.0;

MATCH (c1:Customer {customer_code: 'C001'}), (so1:SalesOrder {so_number: 'SO-50001'}) MERGE (c1)-[:PLACED]->(so1);
MATCH (so1:SalesOrder {so_number: 'SO-50001'}), (i1:Item {item_code: 'ITM-001'}) MERGE (so1)-[:CONTAINS {quantity: 2, unit_price: 1500.0}]->(i1);

MATCH (c2:Customer {customer_code: 'C002'}), (so2:SalesOrder {so_number: 'SO-50002'}) MERGE (c2)-[:PLACED]->(so2);
MATCH (so2:SalesOrder {so_number: 'SO-50002'}), (i2:Item {item_code: 'ITM-002'}) MERGE (so2)-[:CONTAINS {quantity: 2, unit_price: 900.0}]->(i2);
