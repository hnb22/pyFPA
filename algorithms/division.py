from core.float import CustomFloat
import math

class Division:

    @staticmethod
    def divide_basic(a: CustomFloat, b: CustomFloat, prec: int) -> CustomFloat:
        """
        Divide two CustomFloat numbers using basic long division algorithm.
        
        Mathematical formula:
        (sign_a, exp_a, mant_a) ÷ (sign_b, exp_b, mant_b) = 
        (sign_a XOR sign_b, exp_a - exp_b + bias_adjustment, mant_a ÷ mant_b)
        
        Args:
            a: Dividend (numerator)
            b: Divisor (denominator) 
            prec: Target precision for result
            
        Returns:
            CustomFloat representing a ÷ b
        """
        sign_a, exp_a, mant_a, prec_a = a.tuple
        sign_b, exp_b, mant_b, prec_b = b.tuple
        
        if exp_b == 0 and mant_b == 0:
            exp_bits_result = max(8, int(math.log2(prec)) + 2)
            max_exp = (2 ** exp_bits_result) - 1
            result_sign = sign_a ^ sign_b
            return CustomFloat((result_sign, max_exp, 0, prec))
        
        if exp_a == 0 and mant_a == 0:
            return CustomFloat((0, 0, 0, prec))
        
        result_sign = sign_a ^ sign_b
        
        _, exp_bits_a, mant_bits_a = a.get_bit_allocation()
        _, exp_bits_b, mant_bits_b = b.get_bit_allocation()
        
        exp_bits_result = max(8, int(math.log2(prec)) + 2)
        mant_bits_result = prec - exp_bits_result - 1
        
        bias_a = (2 ** (exp_bits_a - 1)) - 1
        bias_b = (2 ** (exp_bits_b - 1)) - 1
        bias_result = (2 ** (exp_bits_result - 1)) - 1
        
        unbiased_exp_a = exp_a - bias_a
        unbiased_exp_b = exp_b - bias_b
        result_exp_unbiased = unbiased_exp_a - unbiased_exp_b
        
        full_mant_a = (1 << mant_bits_a) + mant_a 
        full_mant_b = (1 << mant_bits_b) + mant_b
        
        scaled_dividend = full_mant_a << mant_bits_result
        
        quotient = scaled_dividend // full_mant_b
        
        quotient_msb = quotient.bit_length()
        
        expected_msb = mant_bits_result
        
        if quotient_msb > expected_msb:
            shift_amount = quotient_msb - expected_msb
            result_exp_unbiased += shift_amount
            normalized_quotient = quotient >> shift_amount
        elif quotient_msb < expected_msb:
            shift_amount = expected_msb - quotient_msb
            result_exp_unbiased -= shift_amount
            normalized_quotient = quotient << shift_amount
        else:
            normalized_quotient = quotient
        
        result_mantissa = normalized_quotient - (1 << mant_bits_result)
        
        result_exp_biased = result_exp_unbiased + bias_result
        
        max_exp = (2 ** exp_bits_result) - 1
        if result_exp_biased >= max_exp:
            return CustomFloat((result_sign, max_exp, 0, prec))
        elif result_exp_biased <= 0:
            return CustomFloat((result_sign, 0, 0, prec))
        
        return CustomFloat((result_sign, result_exp_biased, result_mantissa, prec))

if __name__ == "__main__":
    # Test 4: Small numbers
    g = CustomFloat(0.125, precision=64)
    h = CustomFloat(0.25, precision=64)
    result4 = Division.divide_basic(g, h, prec=64)
    print(f"0.125 ÷ 0.25 = {result4.to_float()} (expected: 0.5)")
    
    # Test 5: High precision
    i = CustomFloat(22.0, precision=128)
    j = CustomFloat(7.0, precision=128)
    result5 = Division.divide_basic(i, j, prec=128)
    print(f"22.0 ÷ 7.0 = {result5.to_float()} (expected: 3.142857...)")
