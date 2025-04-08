import os
import argparse
import sqlite3
import hashlib

def create_table(conn: sqlite3.Connection):
    cursor = conn.cursor()

    cursor.executescript("""
    -- 用户表
    CREATE TABLE IF NOT EXISTS User(
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash VARCHAR(255) NOT NULL,
        email VARCHAR(100) UNIQUE,
        phone_number VARCHAR(20) UNIQUE,
        address TEXT,
        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        user_type TEXT NOT NULL CHECK(user_type IN ('customer', 'merchant'))
    );

    -- 店铺表
    CREATE TABLE IF NOT EXISTS Store(
        store_id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_name VARCHAR(100) NOT NULL,
        owner_id INTEGER NOT NULL,
        store_description TEXT,
        store_status TEXT default 'active' CHECK(store_status IN ('active', 'closed')),
        registration_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (owner_id) REFERENCES User(user_id)
    );

    -- 商品表
    CREATE TABLE IF NOT EXISTS Product(
        product_id INTEGER PRIMARY KEY AUTOINCREMENT,
        store_id INTEGER NOT NULL,
        product_name VARCHAR(255) NOT NULL,
        product_description TEXT,
        price DECIMAL(10,2) NOT NULL,
        stock INTEGER NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT default 'active' CHECK(status IN ('active', 'inactive')),
        FOREIGN KEY (store_id) REFERENCES Store(store_id)
    );

    -- 订单表
    CREATE TABLE IF NOT EXISTS Order_Table (
        order_id INTEGER PRIMARY KEY AUTOINCREMENT,
        buyer_id INTEGER NOT NULL,
        payer_id INTEGER,
        payment_method TEXT CHECK (payment_method IS NULL OR payment_method IN ('credit_card', 'wechat', 'alipay')),
        payment_status TEXT CHECK (payment_status IS NULL OR payment_status IN ('pending', 'success', 'failed')),
        payment_time DATETIME DEFAULT NULL,
        order_status TEXT NOT NULL CHECK (order_status IN ('pending', 'paid', 'shipped', 'completed', 'canceled')),
        total_amount DECIMAL(10,2) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (buyer_id) REFERENCES User(user_id),
        FOREIGN KEY (payer_id) REFERENCES User(user_id)
    );

    -- 订单商品表
    CREATE TABLE IF NOT EXISTS Order_Item (
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price_at_purchase DECIMAL(10,2) NOT NULL,
        PRIMARY KEY (order_id, product_id),
        FOREIGN KEY (order_id) REFERENCES Order_Table(order_id),
        FOREIGN KEY (product_id) REFERENCES Product(product_id)
    );

    -- 评价表
    CREATE TABLE IF NOT EXISTS Review (
        review_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        comment_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        rating INTEGER CHECK (rating is NULL OR (rating BETWEEN 1 AND 5)),
        comment TEXT,
        reply TEXT,           
        reply_time DATETIME,
        FOREIGN KEY (user_id) REFERENCES User(user_id),
        FOREIGN KEY (product_id) REFERENCES Product(product_id)
    );

    -- 商品分类表
    CREATE TABLE IF NOT EXISTS Category (
        category_id INTEGER PRIMARY KEY AUTOINCREMENT,
        category_name VARCHAR(100) NOT NULL,
        parent_category_id INTEGER NULL,
        FOREIGN KEY (parent_category_id) REFERENCES Category(category_id)
    );

    -- 商品标签表
    CREATE TABLE IF NOT EXISTS Product_Tag (
        product_id INTEGER NOT NULL,
        category_id INTEGER NOT NULL,
        PRIMARY KEY (product_id, category_id),
        FOREIGN KEY (product_id) REFERENCES Product(product_id),
        FOREIGN KEY (category_id) REFERENCES Category(category_id)
    );

    -- 物流信息表
    CREATE TABLE IF NOT EXISTS Shipping (
        shipping_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        tracking_number VARCHAR(50) UNIQUE NOT NULL,
        carrier VARCHAR(50) NOT NULL,
        shipping_status TEXT NOT NULL CHECK (shipping_status IN ('pending', 'shipped', 'in_transit', 'delivered')),
        estimated_arrival DATETIME,
        actual_arrival DATETIME,
        recipient_name VARCHAR(50) NOT NULL,
        recipient_phone VARCHAR(20) NOT NULL,
        shipping_address TEXT NOT NULL,
        FOREIGN KEY (order_id) REFERENCES Order_Table(order_id)
    );

    -- 物流轨迹表
    CREATE TABLE IF NOT EXISTS Shipping_Track (
        shipping_id INTEGER NOT NULL, 
        track_id INTEGER NOT NULL,
        status TEXT NOT NULL CHECK (status IN ('sorting', 'picked_up', 'in_transit', 'delivered')),
        location TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (shipping_id, track_id),
        FOREIGN KEY (shipping_id) REFERENCES Shipping(shipping_id)
    );                                                                           
    """)

    def get_password_hash(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
    users = [('小明', get_password_hash('123456'), 'merchant'),
             ('小红', get_password_hash('234567'), 'merchant'),
             ('小刚', get_password_hash('345678'), 'merchant'),
             ('小李', get_password_hash('456789'), 'merchant'),
             ('小华', get_password_hash('567890'), 'merchant'),
             ('Jack', get_password_hash('678901'), 'customer'),
             ('Peter', get_password_hash('789012'), 'customer'),
             ('Jim', get_password_hash('789012'), 'customer'),
             ('Mick', get_password_hash('890123'), 'customer'),
             ('Sarra', get_password_hash('901234'), 'customer')]

    for user in users:
        cursor.executescript(f"""
            -- 学生数据
            INSERT or IGNORE INTO User(username, password_hash, user_type) VALUES
            ('{user[0]}', '{user[1]}', '{user[2]}');
        """)
        
    cursor.executescript("""
    -- 店铺数据
    INSERT or IGNORE INTO Store(store_name, owner_id, store_description, store_status) VALUES
    ('亚狮龙旗舰店', 1, '羽毛球物品', 'active'),
    ('华为旗舰店', 1, '盗版华为手机专卖店', 'closed'),
    ('天天果园', 2, '果蔬生鲜超市', 'active'),
    ('小米旗舰店', 3, '小米手机专卖店', 'active'),
    ('五金', 3, '五金店', 'active'),
    ('新居助手', 3, '家用电器', 'active'),
    ('及时雨药房', 4, '药品零售店', 'active'),
    ('世界衣柜', 5, '衣物批发市场', 'active'),
    ('乐活时尚', 5, '时尚品牌连锁店', 'close');

    -- 商品数据
    INSERT or IGNORE INTO Product(store_id, product_name, product_description, price, stock) VALUES
    (1, '羽毛球拍', '天斧七代', 700, 10),
    (1, '羽毛球鞋', '尤尼克斯高仿', 500, 20),
    (1, '桶装羽毛球', '76速12只装', 100, 10),
    (3, '西瓜', '新疆无籽西瓜', 20, 30),
    (3, '红苹果', '富士山红苹果', 5, 30),
    (4, '小米15Ultra', '小米15Ultra 128G', 7000, 100),
    (5, '公牛排插', '8孔公牛排插', 20, 1000),
    (6, '洗衣机', '全自动洗衣机', 450, 200),
    (7, '肠炎宁', '消炎止泻', 50, 100),
    (7, '布洛芬', '退烧止痛', 50, 100),
    (8, '男士短袖T恤', '欧美男士短袖T恤', 150, 100);
                         
    -- 订单数据
    INSERT or IGNORE INTO Order_Table(buyer_id, payer_id, payment_method, payment_status, payment_time, order_status, total_amount, created_at) VALUES
    (6, 6, 'wechat', 'success', '2025-04-04 15:30:00', 'paid', 100, '2025-04-04 15:28:00'),
    (7, 7, 'alipay', 'success', '2025-04-01 02:00:00', 'completed', 6998, '2025-04-01 01:55:43'),
    (8, 8, 'credit_card', 'failed', '2025-04-02 19:33:00', 'pending', 57.8, '2025-04-02 18:00:00'),
    (9, 10, 'wechat', 'success', '2025-04-05 20:32:00', 'shipped', 100, '2025-04-05 20:19:50');

    -- 订单商品数据
    INSERT or IGNORE INTO Order_Item(order_id, product_id, quantity, price_at_purchase) VALUES
    (1, 1, 1, 100),
    (2, 6, 1, 7000),
    (3, 4, 3, 20),
    (4, 11, 1, 150);
                         
    -- 评价数据
    INSERT or IGNORE INTO Review(user_id, product_id, comment_time, rating, comment, reply, reply_time) VALUES
    (7, 6, '2025-04-03 12:00:00', 4, '雷军 yyds!', NULL, NULL),
    (6, 1, '2025-04-05 17:55:12', 1, '发货太慢，客服态度也很差', '很抱歉d，我们会加快发货速度的，请耐心等待', '2025-04-05 18:00:00');

    -- 商品分类数据
    INSERT or IGNORE INTO Category(category_name, parent_category_id) VALUES
    ('电子产品', NULL),
    ('休闲运动', NULL),
    ('食品', NULL),
    ('服装', NULL),          
    ('医药', NULL),          
    ('生活家居', NULL);

    -- 商品标签数据
    INSERT or IGNORE INTO Product_Tag(product_id, category_id) VALUES
    (1, 2),
    (2, 2),
    (3, 2),
    (4, 3),
    (5, 3),
    (6, 1),            
    (7, 6),
    (8, 6),
    (9, 5),
    (10, 5),
    (11, 4);                

    -- 物流信息数据
    INSERT or IGNORE INTO Shipping(order_id, tracking_number, carrier, shipping_status, estimated_arrival, actual_arrival, recipient_name, recipient_phone, shipping_address) VALUES
    (1, '1234567890', '顺丰快递', 'pending', '2025-04-05 10:30:00', NULL, 'I am not Jack', '13800138000', '北京市海淀区北京大学'),
    (2, '2345678901', '圆通快递', 'delivered', '2025-04-03 10:00:00', '2025-04-03 09:33:00', 'Jimmy is on fire', '15800138000', '北京市海淀区清华大学'),
    (4, '3456789012', '京东快递', 'in_transit', '2025-04-06 18:30:00', NULL, 'Michal', '13700137000', '北京市海淀区中国科学院大学');

    -- 物流轨迹数据
    INSERT or IGNORE INTO Shipping_Track(shipping_id, track_id, status, location, timestamp) VALUES
    (1, 1, 'sorting', '天津市', '2025-04-04 15:30:00'),
    (2, 1, 'sorting', '上海市', '2025-04-01 02:30:00'),
    (2, 2, 'picked_up', '上海市', '2025-04-01 02:45:00'),
    (2, 3, 'in_transit', '河南省', '2025-04-02 10:30:00'),
    (2, 4, 'delivered', '北京市', '2025-04-03 09:33:00'),
    (3, 1, 'sorting', '广东市', '2025-04-05 20:32:00'),
    (3, 2, 'picked_up', '广东市', '2025-04-05 20:37:00'),
    (3, 3, 'in_transit', '湖北省', '2025-04-06 10:30:00'); 

    """)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--db', type=str, default='data/test.db', help='database file name')
    args = parser.parse_args()

    conn = sqlite3.connect(args.db)
    print('Opened database successfully')
    create_table(conn)
    print('Table created successfully')
    conn.close()