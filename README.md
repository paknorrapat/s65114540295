# ระบบจัดการคลินิกทันตกรรมสปาร์คกี้ 
65114540295 นรภัทร พันรอบ
วิชา Selected Topics in Software Innovation

#mysql ติดตั้งโดยใช้ scoop 
1.ตั้งค่า environment > path
2.C:\Users\Advice KH\scoop\apps\mysql\current\bin\
3.เช็ค mysql –version ต้องขึ้นแบบนี้
C:\Users\Advice KH>mysql --version
C:\Users\Advice KH\scoop\apps\mysql\current\bin\mysql.exe  Ver 9.0.0 for Win64 on x86_64 (MySQL Community Server - GPL)
4.เปิดสอง terminal
#terminal1
mysqld –console
#terminal2
mysql -u root -p 
show databases;
CREATE DATABASE sparky;

#สร้างโฟลเดอร์ปกติหรือ mkdir …
1.git clone https://github.com/paknorrapat/65114540295-select-topic.git
2.cd 65114540295-select-topic
3.docker-compose up --build
