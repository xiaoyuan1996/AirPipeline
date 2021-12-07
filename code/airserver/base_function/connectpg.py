import os
import time

import globalvar
import psycopg2
import psycopg2.extras
import psycopg2.pool
import util

logger = globalvar.get_value("logger")

try:
    from common.parse_config import get_config
except:
    import sys

    sys.path.append("..")
    from common.parse_config import get_config


class pg_db(object):
    def __init__(self):
        print("init database ...")
        self.db_host = get_config("database", "dbhost")
        self.db_minconn = get_config("database", "minconn")
        self.db_maxconn = get_config("database", "maxconn")
        self.db_user = get_config("database", "user")
        self.db_password = get_config("database", "password")
        self.db_name = get_config("database", "dbname")
        self.db_port = get_config("database", "port")

        try:
            self.conn_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=self.db_minconn,
                maxconn=self.db_maxconn,
                host=self.db_host,
                user=self.db_user,
                password=self.db_password,
                dbname=self.db_name,
                port=self.db_port,
                cursor_factory=psycopg2.extras.DictCursor)

        except (Exception, psycopg2.DatabaseError) as error:
            print("Error while connecting to PostgreSQL", error)

        # 初始化数据库
        self.create_correspond_data()
        self.add_status_tab()
        self.add_internal_template()

    def create_correspond_data(self):
        conn = self.get_instance()
        cur = conn.cursor()

        # 创建airpipline_codetable
        cur.execute('''CREATE TABLE IF NOT EXISTS airpipline_codetab
        (id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        version TEXT NOT NULL,
        status_id INT NOT NULL,
        create_time TEXT NOT NULL,
        code_path TEXT NOT NULL,
        user_id INT NOT NULL,
        dist  BOOL NOT NULL,
        description TEXT
        );
        ''')

        # 创建airpipline_trainjobtable
        cur.execute('''CREATE TABLE IF NOT EXISTS airpipline_trainjobtab
        (id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        user_id INT NOT NULL,
        code_path TEXT NOT NULL,
        data_path TEXT NOT NULL,
        model_path TEXT NOT NULL,
        visual_path TEXT NOT NULL,
        image_id INT NOT NULL,
        create_time TEXT NOT NULL,       
        status_id INT NOT NULL,
        dist  BOOL NOT NULL,
        description TEXT,
        params JSON,
        task_id TEXT
        );
        ''')

        # 创建airpipline_debugtable
        cur.execute('''CREATE TABLE IF NOT EXISTS airpipline_debugtab
        (id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        user_id INT NOT NULL,
        image_id INT NOT NULL,
        create_time TEXT NOT NULL,
        status_id INT NOT NULL,
        code_path TEXT,
        data_path TEXT,
        description TEXT,
        debug_user_name TEXT NOT NULL,
        debug_user_pw TEXT NOT NULL,
        host_port int NOT NULL 
        );
        ''')

        # 创建airpipline_notebooktable
        cur.execute('''CREATE TABLE IF NOT EXISTS airpipline_notebooktab
        (id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        user_id INT NOT NULL,
        image_id INT NOT NULL,
        create_time TEXT NOT NULL,
        status_id INT NOT NULL,
        code_path TEXT,
        data_path TEXT,
        description TEXT
        );
        ''')

        # 创建airpipline_templatetable
        cur.execute('''CREATE TABLE IF NOT EXISTS airpipline_templatetab
        (id SERIAL PRIMARY KEY,
        name TEXT NOT NULL,
        user_id INT NOT NULL,
        image_id INT NOT NULL,
        code_path TEXT NOT NULL,
        model_path TEXT ,
        create_time TEXT NOT NULL,
        privilege INT NOT NULL,
        description TEXT
        );
        ''')

        # 创建airpipline_statustable
        cur.execute('''CREATE TABLE IF NOT EXISTS airpipline_statustab
        (id INT PRIMARY KEY,
        status TEXT
        );
        ''')

        # 创建DebugTableTable
        # 创建ModelTable

        conn.commit()
        cur.close()
        self.put_instance(conn)

    def add_status_tab(self):
        # 插入状态数据
        try:  # 如果不存在
            sql = "insert into airpipline_statustab (id, status) values  (0,'privilege-官方')"
            flag, data = self.insert(sql)
            sql = "insert into airpipline_statustab (id, status) values  (1,'privilege-私有')"
            flag, data = self.insert(sql)
            sql = "insert into airpipline_statustab (id, status) values  (2,'privilege-公开')"
            flag, data = self.insert(sql)
            sql = "insert into airpipline_statustab (id, status) values  (50,'停止')"
            flag, data = self.insert(sql)
            sql = "insert into airpipline_statustab (id, status) values  (100,'初始化')"
            flag, data = self.insert(sql)
            sql = "insert into airpipline_statustab (id, status) values  (150,'暂停')"
            flag, data = self.insert(sql)
            sql = "insert into airpipline_statustab (id, status) values  (200,'运行正常')"
            flag, data = self.insert(sql)
            sql = "insert into airpipline_statustab (id, status) values  (400,'运行失败')"
            flag, data = self.insert(sql)
        except:
            pass

    def add_internal_template(self):
        # 增加默认模板
        internal_template_path = os.path.join(get_config('path', 'airpipline_path'), "internal", "template")

        all_default_templates = os.listdir(internal_template_path)

        for template in all_default_templates:
            cur_template_path = os.path.join(internal_template_path, template)

            # 检查数据完备性
            cur_files = os.listdir(cur_template_path)
            if "code" not in cur_files:
                logger.info("code not found in {}".format(cur_template_path))
                continue
            elif "model" not in cur_files:
                logger.info("model not found in {}".format(cur_template_path))
                continue
            elif "template.json" not in cur_files:
                logger.info("template.json not found in {}".format(cur_template_path))
                continue

            # 读取检查template.json
            template_info = util.read_json(os.path.join(cur_template_path, "template.json"))
            if ("template_name" not in template_info.keys()) or ("image_name" not in template_info.keys()) \
                    or ("image_id" not in template_info.keys()) or ("description" not in template_info.keys()):
                logger.info("template.json must include: template_name, image_name, image_id and description")
                continue

            # 检查template是否在数据库中
            read_sql = "select id from airpipline_templatetab where name='{0}' and privilege=0".format(
                template_info['template_name'])
            flag, query_info = self.query_one(read_sql)
            if query_info == None:
                # 插表
                create_time = str(time.strftime('%Y-%m-%d %H:%M:%S'))
                sql = "insert into airpipline_templatetab (name,user_id,image_id,code_path,model_path,create_time,privilege,description) values  ('{0}',{1},{2},'{3}','{4}','{5}',{6},'{7}')".format(
                    template_info['template_name'], 0, template_info['image_id'],
                    os.path.join(cur_template_path, 'code'), os.path.join(cur_template_path, 'model'), create_time, "0",
                    template_info['description'])
                code, data = self.insert(sql)

    def get_instance(self):
        return self.conn_pool.getconn()

    def put_instance(self, conn):
        self.conn_pool.putconn(conn)

    def insert(self, sql):
        conn = self.get_instance()
        cur = conn.cursor()
        try:
            flag = True
            cur.execute(sql)
            info = cur.statusmessage
            conn.commit()
        except psycopg2.errors.UniqueViolation as error:
            raise error
            flag = False
            info = '插入失败,本条目已经存在'
            conn.rollback()
        except (Exception, psycopg2.Error) as error:
            raise error
            flag = False
            info = '插入失败'
            conn.rollback()
        finally:
            cur.close()
            self.put_instance(conn)
            return flag, info

    def insert_return_id(self, sql):
        conn = self.get_instance()
        cur = conn.cursor()
        try:
            flag = True
            cur.execute(sql)
            cur.statusmessage
            conn.commit()
            return_id = cur.fetchone()
            info = {"return_id": return_id}
        except psycopg2.errors.UniqueViolation as error:
            raise error
            flag = False
            info = '插入失败,本条目已经存在'
            conn.rollback()
        except (Exception, psycopg2.Error) as error:
            raise error
            flag = False
            info = '插入失败'
            conn.rollback()
        finally:
            cur.close()
            self.put_instance(conn)
            return flag, info

    def delete(self, sql):
        conn = self.get_instance()
        cur = conn.cursor()
        try:
            flag = True
            cur.execute(sql)
            info = cur.statusmessage
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            flag = False
            raise error
            info = '删除失败'
            conn.rollback()
        finally:
            cur.close()
            self.put_instance(conn)
            return flag, info

    def update(self, sql):
        conn = self.get_instance()
        cur = conn.cursor()
        try:
            flag = True
            cur.execute(sql)
            info = cur.statusmessage
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            flag = False
            raise error
            info = "更新失败"
            conn.rollback()
        finally:
            cur.close()
            self.put_instance(conn)
            return flag, info

    def query_all(self, sql):
        conn = self.get_instance()
        cur = conn.cursor()
        try:
            flag = True
            cur.execute(sql)
            info = cur.fetchall()
        except (Exception, psycopg2.Error) as error:
            raise error
            info = '查询出错'
            flag = False
        finally:
            cur.close()
            self.put_instance(conn)
            return flag, info

    def query_one(self, sql):
        conn = self.get_instance()
        cur = conn.cursor()
        try:
            flag = True
            cur.execute(sql)
            info = cur.fetchone()
        except (Exception, psycopg2.Error) as error:
            raise error
            info = '查询出错'
            flag = False
        finally:
            cur.close()
            self.put_instance(conn)
            return flag, info

    def query_limit_offset(self, sql, page_size, page_num):
        conn = self.get_instance()
        cur = conn.cursor()
        try:
            flag = True
            cur.execute(sql)
            count = (len(cur.fetchall()))
            sql_limit_offset = sql + " limit {0} offset {1}".format(page_size,
                                                                    page_size * (
                                                                            page_num - 1))
            cur.execute(sql_limit_offset)
            info = cur.fetchall()
        except (Exception, psycopg2.Error) as error:
            raise error
            info = '查询出错'
            flag = False
            count = 0
        finally:
            cur.close()
            self.put_instance(conn)
            return flag, info, count


DB = pg_db()
globalvar.set_value("DB", DB)

if __name__ == '__main__':
    DB = pg_db()
    # print(DB.update('update testjson set id=4 where id=3'))

    # data = DB.query_one("select * from doctab")
    # print(data)
