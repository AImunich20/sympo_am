from flask import Flask, request, render_template
from lunar_core import function_thai
import contextlib
from io import StringIO
import json

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        try:
            y = int(request.form["y"])
            m = int(request.form["m"])
            d = int(request.form["d"])

            buf = StringIO()
            with contextlib.redirect_stdout(buf):
                ret = function_thai([(y, m, d)])

            printed = buf.getvalue().strip()

            if ret is None:
                # ฟังก์ชันไม่ได้ return → ใช้ข้อความที่พิมพ์ออกมา
                result = printed if printed else "function_thai ไม่ได้คืนค่า (None) และไม่มีข้อความพิมพ์ออกมา"
            else:
                # ฟังก์ชันคืนค่า → แสดงผลอย่างสวยงาม
                if isinstance(ret, (dict, list, tuple)):
                    result = json.dumps(ret, ensure_ascii=False, indent=2)
                else:
                    result = str(ret)

        except Exception as e:
            error = str(e)

    return render_template('index.html', result=result, error=error)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
