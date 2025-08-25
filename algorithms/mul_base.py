import math
from core.float import CustomFloat

class BasicMultiplication:

    @staticmethod
    def multiple(a: CustomFloat, b: CustomFloat) -> CustomFloat:
        sign_a, exp_a, mant_a, prec_a = a.tuple
        sign_b, exp_b, mant_b, prec_b = b.tuple

        result_sign = sign_a ^ sign_b # XOR for sign multiplication
        
        # Get bit allocations for both operands and result
        _, exp_bits_a, mant_bits_a = a.get_bit_allocation()
        _, exp_bits_b, mant_bits_b = b.get_bit_allocation()

        # Calculate exponent (subtract bias, add, then re-bias for result precision)
        bias_a = (2 ** (exp_bits_a - 1)) - 1
        bias_b = (2 ** (exp_bits_b - 1)) - 1

        # Get bit allocation
        exp_bits_result = int(math.log2(prec_a))
        mant_bit_result = prec_a - exp_bits_result - 1

        # Unbiased exponents
        unbiased_exp_a = exp_a - bias_a
        unbiased_exp_b = exp_b - bias_b
        
        # Add exponents (multiplication rule: a^m * a^n = a^(m+n))
        result_exp_unbiased = unbiased_exp_a + unbiased_exp_b

        #Multiply mantissa
        full_mant_a = (1 << mant_bits_a) + mant_a  # 1.mantissa_a as integer
        full_mant_b = (1 << mant_bits_b) + mant_b  # 1.mantissa_b as integer

        # Multiply full mantissas
        product = full_mant_a * full_mant_b

if __name__ == "__main__":
    a = CustomFloat(3.5, precision=64)
    b = CustomFloat(2.0, precision=64)
    result = multiply(a, b)

    print(result)