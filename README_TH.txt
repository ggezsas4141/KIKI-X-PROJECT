KIKI X PROJECT V4 — สร้างไฟล์ EXE เดียวผ่าน GitHub Actions

สิ่งที่จะได้:
  KIKI_X_PROJECT_V4.exe (ไฟล์เดียวสำหรับเปิดใช้งานบน Windows)

ข้อจำกัดสำคัญ:
  แพ็กนี้เป็นซอร์สพร้อม workflow สำหรับให้ GitHub สร้าง EXE บน Windows
  ไม่ใช่ไฟล์ EXE ที่คอมไพล์เสร็จแล้ว เนื่องจากสภาพแวดล้อมที่จัดทำแพ็กนี้ไม่ใช่ Windows

วิธีสร้าง EXE:
1. เข้าสู่ GitHub และสร้าง repository ใหม่ (เลือก Private ได้)
2. อัปโหลดไฟล์ทั้งหมดในโฟลเดอร์นี้ รวมทั้งโฟลเดอร์ .github/workflows/build-windows.yml
   ให้ไฟล์ KIKI_X_PROJECT_V4.py และ requirements.txt อยู่ที่ root ของ repository
3. ไปที่แท็บ Actions แล้วเลือก "Build Windows EXE"
4. ถ้า workflow ยังไม่เริ่ม ให้กด "Run workflow"
5. รอจนงานสำเร็จ แล้วเปิดงานล่าสุดและดาวน์โหลด Artifact ชื่อ
   KIKI_X_PROJECT_V4-Windows-EXE
6. แตก ZIP artifact ที่ดาวน์โหลด จะพบ KIKI_X_PROJECT_V4.exe

Workflow จะทำงานอัตโนมัติเมื่อ push ไปยัง main หรือ master ด้วย

ความปลอดภัย:
- ตรวจสอบโค้ดและสแกนไฟล์ EXE ก่อนเปิดใช้งาน
- ไม่จำเป็นต้องเปิดโปรแกรมด้วยสิทธิ์ Administrator สำหรับการใช้งานทั่วไป
- ปุ่ม Clean TEMP ลบไฟล์ TEMP เก่ากว่า 24 ชั่วโมงและไม่สามารถกู้คืนจากแอปได้
- ฟังก์ชันปรับ Registry ควรใช้ด้วยความเข้าใจ และเก็บข้อมูลสำรองไว้
