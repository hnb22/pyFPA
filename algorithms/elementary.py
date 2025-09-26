from core.float import CustomFloat
from algorithms.multiplication import Multiplication
from algorithms.division import Division
from algorithms.addition import Addition

class Elementary:

    @staticmethod
    def sin_taylor(x: CustomFloat) -> CustomFloat:
        sign, exp, mant, prec = x.tuple

        result = x
        term = x
        n = 1
        x2 = Multiplication.multiply_basic(x, x, prec)
        negx2 = CustomFloat((x2.sign ^ 1, x2.exponent, x2.mantissa, x2.precision_bits))
        while True:
            denom_raw = (2*n)*(2*n+1)
            denom_flt = CustomFloat(float(denom_raw), precision=prec)

            term = Multiplication.multiply_basic(term, negx2, prec)
            term = Division.divide_basic(term, denom_flt, prec)

            result = Addition.add_basic(result, term)

            if Elementary.is_negligible(term, result, prec):
                break
            
            n += 1

        return result
    
    @staticmethod
    def is_negligible(term: CustomFloat, result: CustomFloat, prec: int) -> bool:
        if term.exponent == 0 and term.mantissa == 0: 
            return True
        
        if result.exponent - term.exponent > prec // 4:
            return True
            
        return False