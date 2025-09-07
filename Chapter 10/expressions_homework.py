from abc import ABC, abstractmethod
from typing import Any, Self, Sequence

from numpy import isin
import math


class Expression(ABC):
    """
    Abstract for any expression
    """

    def __init__(self, *args):
        self.args = args

    def _check_number(self, rhs: Any):
        if isinstance(rhs, (float, int)):
            rhs = Number(rhs)
        return rhs

    def __add__(self, rhs: "Expression|float"):
        rhs = self._check_number(rhs)
        return Sum(self, rhs)

    def __radd__(self, lhs: "Expression|float"):
        return self.__add__(lhs)

    def __neg__(self):
        return Negative(self)

    def __sub__(self, rhs: "Expression|float"):
        rhs = self._check_number(rhs)
        return Difference(self, rhs)

    def __rsub__(self, lhs: "Expression|float"):
        lhs = self._check_number(lhs)
        return Difference(lhs, self)

    def __mul__(self, rhs: "Expression|float"):
        rhs = self._check_number(rhs)
        return Product(self, rhs)

    def __rmul__(self, lhs: "Expression|float"):
        lhs = self._check_number(lhs)
        return Product(lhs, self)

    def __truediv__(self, rhs: "Expression|float"):
        rhs = self._check_number(rhs)
        return Quotinent(self, rhs)

    def __rtruediv__(self, lhs: "Expression|float"):
        lhs = self._check_number(lhs)
        return Quotinent(lhs, self)

    def __pow__(self, rhs: "Expression|float"):
        rhs = self._check_number(rhs)
        return Power(self, rhs)

    def __rpow__(self, lhs: "Expression|float"):
        lhs = self._check_number(lhs)
        return Power(lhs, self)

    def __call__(self, rhs: "Expression|float"):
        if not isinstance(self, Function):
            raise ValueError("Can only call functions")
        rhs = self._check_number(rhs)
        return Apply(self, rhs)

    def _repr_nested(self, level=1):
        args_repr = ", ".join(
            [
                a._repr_nested(level + 1) if hasattr(a, "_repr_nested") else f"{a}"
                for a in self.args
            ]
        )
        padding = " " * level
        return f"{self.__class__.__name__}(\n{padding}{args_repr}\n{padding[:-1]})"

    def __repr__(self) -> str:
        return self._repr_nested()

    def contains_variable(self, variable: str):
        """
        Recursively searches for particular variables
        """
        if isinstance(self, Variable) and self.args[0] == variable:
            return True
        return any(
            hasattr(a, "contains_variable") and a.contains_variable(variable)
            for a in self.args
        )

    def distinct_functions(self):
        """
        Build a set of all included functions by their names
        """
        result = set()
        if isinstance(self, Function):
            result.add(self.name)
        for a in self.args:
            if hasattr(a, "distinct_functions"):
                result = result.union(a.distinct_functions())
        return result

    def contains_operator(self, op: type["Expression"]):
        if isinstance(self, op):
            return True
        for a in self.args:
            if hasattr(a, "contains_operator") and a.contains_operator(op):
                return True
        return False

    def contains_sum(self):
        return self.contains_operator(Sum)

    def _latex_args_(self, args: Sequence) -> list[str]:
        return [
            a._compile_latex_() if hasattr(a, "_compile_latex_") else f"{a}"
            for a in args
        ]

    @abstractmethod
    def _compile_latex_(self) -> str:
        """
        Represent as latex formula
        """

    def _repr_latex_(self) -> str:
        return f"$${self._compile_latex_()}$$"

    def _python_args(self, args: Sequence) -> list[str]:
        return [
            a._python_expr() if hasattr(a, "_python_expr") else f"{a}" for a in args
        ]

    @abstractmethod
    def _python_expr(self) -> str:
        """
        Represent as pythonic expression (for eval)
        """

    def python_function(self, **kwargs):
        expr = self._python_expr()
        return eval(expr, {**kwargs, "math": math})


class Sum(Expression):
    """
    Sum expression
    """

    def _compile_latex_(self):
        args = "+".join(self._latex_args_(self.args))
        return f"{args}"

    def _python_expr(self):
        return "+".join(self._python_args(self.args))


class Negative(Expression):
    def _compile_latex_(self):
        return f"-{self._latex_args_(self.args)}"

    def _python_expr(self):
        return f"-{self._python_args(self.args)}"


class Difference(Expression):
    def _compile_latex_(self):
        args = "-".join(self._latex_args_(self.args))
        return f"{args}"

    def _python_expr(self):
        return "-".join(self._python_args(self.args))


class Product(Expression):
    """
    Product
    """

    def _compile_latex_(self):
        args = "".join(self._latex_args_(self.args))
        return f"{args}"

    def _python_expr(self):
        return "*".join(self._python_args(self.args))


class Quotinent(Expression):
    def _compile_latex_(self):
        args = "".join(f"{{{a}}}" for a in self._latex_args_(self.args))
        return f"\\frac{args}"

    def _python_expr(self):
        return "/".join(self._python_args(self.args))


class Power(Expression):
    def _compile_latex_(self):
        args = "^".join(self._latex_args_(self.args))
        return f"{args}"

    def _python_expr(self):
        return "**".join(self._python_args(self.args))


class SquareRoot(Expression):
    def _compile_latex_(self):
        power, *args = self.args
        args = "".join(self._latex_args_(args))
        return f"\\sqrt[{power}]{{{args}}}"

    def _python_expr(self):
        power, *args = self.args
        args = "".join(self._python_args(args))
        return f"math.pow({args}, 1/{power})"


class Apply(Expression):
    def _compile_latex_(self):
        fn, *args = self.args
        args = ", ".join(self._latex_args_(args))
        if isinstance(fn, Function):
            return f"{fn.name}({args})"
        return ""

    def _python_expr(self):
        fn, *args = self.args
        args = ", ".join(self._python_args(args))
        if isinstance(fn, Function):
            return f"math.{fn.name}({args})"
        return ""


class Variable(Expression):
    def _repr_nested(self, level=1):
        return self.args[0]

    def _compile_latex_(self):
        return self.name

    def _python_expr(self):
        return f"({self.name})"

    @property
    def name(self):
        return self.args[0]


class Number(Expression):
    def _repr_nested(self, level=1):
        return f"{self.args[0]}"

    @property
    def value(self):
        return self.args[0]

    def _compile_latex_(self):
        return f"{self.value}"

    def _python_expr(self):
        return f"({self.value})"


class Function(Expression):
    def _repr_nested(self, level=1):
        return self.args[0]

    def _compile_latex_(self):
        return ""

    def _python_expr(self) -> str:
        return ""

    @property
    def name(self):
        return self.args[0]
