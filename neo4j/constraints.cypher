// Uniqueness constraints for pure Inventory Knowledge Graph
CREATE CONSTRAINT unique_asset_tag IF NOT EXISTS FOR (a:Asset) REQUIRE a.asset_tag IS UNIQUE;
CREATE CONSTRAINT unique_vendor_code IF NOT EXISTS FOR (v:Vendor) REQUIRE v.vendor_code IS UNIQUE;
CREATE CONSTRAINT unique_item_code IF NOT EXISTS FOR (i:Item) REQUIRE i.item_code IS UNIQUE;
CREATE CONSTRAINT unique_site_code IF NOT EXISTS FOR (s:Site) REQUIRE s.site_code IS UNIQUE;
CREATE CONSTRAINT unique_location_code IF NOT EXISTS FOR (l:Location) REQUIRE l.location_code IS UNIQUE;
CREATE CONSTRAINT unique_customer_code IF NOT EXISTS FOR (c:Customer) REQUIRE c.customer_code IS UNIQUE;
CREATE CONSTRAINT unique_po_number IF NOT EXISTS FOR (po:PurchaseOrder) REQUIRE po.po_number IS UNIQUE;
CREATE CONSTRAINT unique_so_number IF NOT EXISTS FOR (so:SalesOrder) REQUIRE so.so_number IS UNIQUE;
CREATE CONSTRAINT unique_category_name IF NOT EXISTS FOR (cat:Category) REQUIRE cat.name IS UNIQUE;
