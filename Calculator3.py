import sys
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6 import uic

form_class = uic.loadUiType("Calculator3.ui")[0]

#
#
#           100% GPT가 코딩 + 기능적 문제만 지적
#
#


def safe_eval(expr: str) -> float:
    # 완성된 수식을 숫자와 연산자로 분리.
    def parse_tokens(expr):
        tokens = []
        num = ""
        i = 0
        while i < len(expr):
            c = expr[i]
            if c in "0123456789.":
                num += c
            elif c in "+-*/":
                if num:
                    tokens.append(float(num))
                    num = ""

                if c == "-" and (i == 0 or expr[i - 1] in "+-*/"):#'-'음수 구분
                    num = "-"
                else:
                    tokens.append(c)
            i += 1

        tokens.append(float(num))

        return tokens
    
    # 가공한 데이터에서 연산자를 기준으로 양 옆 숫자 연산 후 해당 자리에 저장.
    def apply_ops(tokens, ops):
        i = 0
        while i < len(tokens):
            if tokens[i] in ops:
                op = tokens[i]
                left = tokens[i - 1]
                right = tokens[i + 1]

                if op == "+":
                    result = left + right
                elif op == "-":
                    result = left - right
                elif op == "*":
                    result = left * right
                elif op == "/":
                    result = left / right

                tokens[i - 1:i + 2] = [result]
                i = 0
            else:
                i += 1

        return tokens

    # 실제로 돌아가는 부분.
    tokens = parse_tokens(expr)
    tokens = apply_ops(tokens, {"*", "/"})
    tokens = apply_ops(tokens, {"+", "-"})
    return tokens[0]


# 연산자와 부호(-) 구분하기
def find_last_true_operator(expr: str) -> int:
    for i in range(len(expr) - 1, -1, -1):
        if expr[i] in "+*/":
            return i
        elif expr[i] == "-":
            if i > 0 and expr[i - 1] not in "+-*/":
                return i
    return -1


class Calculator(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.expression = ""
        self.setup_connections()

    # 클릭과 함수 연결부
    def setup_connections(self):
        for i in range(10):
            getattr(self, f"button_{i}").clicked.connect(lambda _, x=i: self.input_number(str(x)))

        self.btn_add.clicked.connect(lambda: self.input_operator("+"))
        self.btn_sub.clicked.connect(lambda: self.input_operator("-"))
        self.btn_mul.clicked.connect(lambda: self.input_operator("*"))
        self.btn_div.clicked.connect(lambda: self.input_operator("/"))
        self.btn_dot.clicked.connect(self.input_dot)
        self.btn_tog.clicked.connect(self.toggle_sign)

        self.btn_eq.clicked.connect(self.calculate_result)
        self.btn_ac.clicked.connect(self.clear_all)
        self.btn_ce.clicked.connect(self.clear_last)

        #self.btn_ce.setText("⌫")

    # 숫자 입력
    def input_number(self, num):
        self.auto_clear_if_result()

        if self.expression and self.expression[-1] == "0" and (len(self.expression) == 1 or self.expression[-2] in "+-*/"):
            self.expression = self.expression[:-1] + num
        else:
            self.expression += num

        self.update_display()

    # 연산자 입력
    def input_operator(self, op):
        self.auto_clear_if_result()

        if not self.expression:
            if op == "-":
                self.expression = "-"
                self.update_display()
            return

        if self.expression == "-" and op != "-":
            return

        last = self.expression[-1]
        if last in "+-*/":
            if last == "-" and len(self.expression) >= 2 and self.expression[-2] in "+*/":
                return
            self.expression = self.expression[:-1] + op
        else:
            self.expression += op

        self.update_display()

    # . 입력
    def input_dot(self):
        self.auto_clear_if_result()

        if not self.expression or self.expression[-1] in "+-*/":
            self.expression += "0."
            self.update_display()
            return
        
        for i in range( (len(self.expression) - 1), -1, -1):
            if self.expression[i] in "+-*/":
                break
            if self.expression[i] == ".":
                return
            
        self.expression += "."
        self.update_display()

    # +/- 입력
    def toggle_sign(self):
        self.auto_clear_if_result()

        if not self.expression:
            self.expression = "-"
            self.update_display()
            return
        if self.expression == "-":
            self.expression = ""
            self.update_display()
            return
        
        last_op = find_last_true_operator(self.expression)
        token = self.expression[last_op + 1:]
        new_token = token[1:] if token.startswith("-") else "-" + token
        
        self.expression = self.expression[:last_op + 1] + new_token
        self.update_display()

    # = 입력
    def calculate_result(self):
        self.line_top.setText(self.expression)

        if not self.expression or self.expression[-1] in "+-*/":
            return

        try:
            result = safe_eval(self.expression)
        except Exception:
            self.expression = "Error"
            self.update_display()
            return

        # 결과 표시 형식 설정
        if abs(result) > 1e10 and result == int(result):
            display = str(int(result))
        else:
            display = f"{result:.10f}".rstrip("0").rstrip(".")

        self.expression = display
        self.update_display()

    # AC 입력
    def clear_all(self):
        self.line_top.setText("")
        self.expression = ""
        self.update_display()

    # CE 입력(backspace)
    def clear_last(self):
        self.auto_clear_if_result()
        self.expression = self.expression[:-1]
        self.update_display()

    # 출력
    def update_display(self):
        self.label_display.setText(self.expression)

    # 글자 유무 확인(에러 유발)
    def auto_clear_if_result(self):
        text = self.label_display.text()
        if any(c not in "0123456789.+-*/" for c in text):
            self.clear_all()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calculator()
    window.show()
    sys.exit(app.exec())
