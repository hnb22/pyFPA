from core.float import CustomFloat
import math

class Addition:

    @staticmethod
    def add_basic(a: CustomFloat, b: CustomFloat) -> CustomFloat:
        """
        Add two CustomFloat numbers using basic addition algorithm.
        
        Algorithm steps:
        1. Handle special cases (zero values)
        2. Align mantissas by adjusting for exponent difference
        3. Add or subtract mantissas based on signs
        4. Normalize the result
        5. Handle overflow/underflow
        """

        sign_a, exp_a, mant_a, prec_a = a.tuple
        sign_b, exp_b, mant_b, prec_b = b.tuple

        result_prec = max(prec_a, prec_b)
        
        exponent_bits = max(8, int(math.log2(result_prec)) + 2)
        mantissa_bits = result_prec - exponent_bits - 1
        exponent_bias = (2 ** (exponent_bits - 1)) - 1

        if exp_a == 0 and mant_a == 0:
            return b
        if exp_b == 0 and mant_b == 0:
            return a

        unbiased_exp_a = exp_a - exponent_bias
        unbiased_exp_b = exp_b - exponent_bias
        exp_diff = unbiased_exp_a - unbiased_exp_b

        full_mant_a = (1 << mantissa_bits) + mant_a
        full_mant_b = (1 << mantissa_bits) + mant_b

        if exp_diff > 0:
            if exp_diff >= mantissa_bits + 5:
                return a
            aligned_mant_a = full_mant_a
            aligned_mant_b = full_mant_b >> exp_diff
            result_unbiased_exp = unbiased_exp_a
        elif exp_diff < 0:
            exp_diff = -exp_diff
            if exp_diff >= mantissa_bits + 5:
                return b
            aligned_mant_a = full_mant_a >> exp_diff
            aligned_mant_b = full_mant_b
            result_unbiased_exp = unbiased_exp_b
        else:
            aligned_mant_a = full_mant_a
            aligned_mant_b = full_mant_b
            result_unbiased_exp = unbiased_exp_a

        if sign_a == sign_b:
            result_mant = aligned_mant_a + aligned_mant_b
            result_sign = sign_a
        else:
            if aligned_mant_a >= aligned_mant_b:
                result_mant = aligned_mant_a - aligned_mant_b
                result_sign = sign_a
            else:
                result_mant = aligned_mant_b - aligned_mant_a
                result_sign = sign_b

        if result_mant == 0:
            return CustomFloat._from_value(0.0, result_prec)

        if result_mant >= (1 << (mantissa_bits + 1)):
            result_mant >>= 1
            result_unbiased_exp += 1

        while result_mant < (1 << mantissa_bits) and result_unbiased_exp > -exponent_bias:
            result_mant <<= 1
            result_unbiased_exp -= 1

        result_mant -= (1 << mantissa_bits)
        
        result_exp = result_unbiased_exp + exponent_bias

        if result_exp <= 0:
            return CustomFloat._from_value(0.0, result_prec)
        if result_exp >= (1 << exponent_bits) - 1:
            return CustomFloat((result_sign, (1 << exponent_bits) - 1, 0, result_prec))

        return CustomFloat((result_sign, result_exp, result_mant, result_prec))
    