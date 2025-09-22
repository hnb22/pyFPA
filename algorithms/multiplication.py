import math
from core.float import CustomFloat

class Multiplication:

    @staticmethod
    def multiply_basic(a: CustomFloat, b: CustomFloat, prec: int) -> CustomFloat:
        """
        Multiply two CustomFloat numbers using basic algorithm.
        
        Mathematical formula:
        (sign_a, exp_a, mant_a) × (sign_b, exp_b, mant_b) = 
        (sign_a XOR sign_b, exp_a + exp_b - bias, mant_a × mant_b with normalization)
        """
        sign_a, exp_a, mant_a, prec_a = a.tuple
        sign_b, exp_b, mant_b, prec_b = b.tuple


        # Handle zero cases
        if (exp_a == 0 and mant_a == 0) or (exp_b == 0 and mant_b == 0):
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
        result_exp_unbiased = unbiased_exp_a + unbiased_exp_b

        full_mant_a = (1 << mant_bits_a) + mant_a  
        full_mant_b = (1 << mant_bits_b) + mant_b  

        product = full_mant_a * full_mant_b
        total_bits = mant_bits_a + mant_bits_b
        
        if product >= (1 << (total_bits + 1)):
            result_exp_unbiased += 1

            shift_amount = total_bits + 1 - mant_bits_result
            if shift_amount >= 0:
                normalized_mantissa = product >> shift_amount
            else:
                normalized_mantissa = product << (-shift_amount)
        else:
            shift_amount = total_bits - mant_bits_result
            if shift_amount >= 0:

                normalized_mantissa = product >> shift_amount
            else:
                normalized_mantissa = product << (-shift_amount)
        
        result_mantissa = normalized_mantissa - (1 << mant_bits_result)
        
        result_exp_biased = result_exp_unbiased + bias_result
        
        max_exp = (2 ** exp_bits_result) - 1
        if result_exp_biased >= max_exp:
            return CustomFloat((result_sign, max_exp, 0, prec))
        elif result_exp_biased <= 0:
            return CustomFloat((result_sign, 0, 0, prec))

        return CustomFloat((result_sign, result_exp_biased, result_mantissa, prec))

    @staticmethod
    def multiply_karat(a: CustomFloat, b: CustomFloat, prec: int) -> CustomFloat:
        """
        Multiply two float numbers using Karatsuba algorithm
        
        Complexity: O(n^1.585)
        
        Formula for CustomFloat tuples (sign_a, exp_a, mant_a, prec_a) × (sign_b, exp_b, mant_b, prec_b):
        
        1. Sign: result_sign = sign_a ⊕ sign_b
        2. Exponent: result_exp = (exp_a - bias_a) + (exp_b - bias_b) + bias_result
        3. Mantissa: Using Karatsuba on full mantissas M_a = (2^n + mant_a), M_b = (2^n + mant_b)
           
           For n-digit numbers x and y, split as:
           x = x₁ × 2^(n/2) + x₀
           y = y₁ × 2^(n/2) + y₀
           
           Karatsuba: x × y = z₂ × 2^n + z₁ × 2^(n/2) + z₀  [3 multiplications]
           where:
           z₂ = x₁ × y₁
           z₀ = x₀ × y₀  
           z₁ = (x₁ + x₀) × (y₁ + y₀) - z₂ - z₀
           
        4. Normalize result mantissa to 1.xxxxx format and adjust exponent if needed
        """
        sign_a, exp_a, mant_a, prec_a = a.tuple
        sign_b, exp_b, mant_b, prec_b = b.tuple

        if (exp_a == 0 and mant_a == 0) or (exp_b == 0 and mant_b == 0):
            return CustomFloat((0, 0, 0, prec))

        sign_result = sign_a ^ sign_b

        _, exp_bits_a, mant_bits_a = a.get_bit_allocation()
        _, exp_bits_b, mant_bits_b = b.get_bit_allocation()

        full_mant_a = (1 << mant_bits_a) + mant_a
        full_mant_b = (1 << mant_bits_b) + mant_b

        n = max(mant_bits_a, mant_bits_b)
        m = n // 2
        
        x1 = full_mant_a >> m
        x0 = full_mant_a & ((1 << m) - 1) 
        
        y1 = full_mant_b >> m 
        y0 = full_mant_b & ((1 << m) - 1)
        
        z2 = x1 * y1              
        z0 = x0 * y0               
        z1 = (x1 + x0) * (y1 + y0) - z2 - z0  
        
        product = (z2 << (2 * m)) + (z1 << m) + z0   
        
        exp_bits_result = max(8, int(math.log2(prec)) + 2)
        mant_bits_result = prec - exp_bits_result - 1
        
        bias_a = (2 ** (exp_bits_a - 1)) - 1
        bias_b = (2 ** (exp_bits_b - 1)) - 1
        bias_result = (2 ** (exp_bits_result - 1)) - 1
        
        unbiased_exp_a = exp_a - bias_a
        unbiased_exp_b = exp_b - bias_b
        result_exp_unbiased = unbiased_exp_a + unbiased_exp_b
        
        total_bits = mant_bits_a + mant_bits_b
        
        if product >= (1 << (total_bits + 1)):
            result_exp_unbiased += 1
            shift_amount = total_bits + 1 - mant_bits_result
            if shift_amount >= 0:
                normalized_mantissa = product >> shift_amount
            else:
                normalized_mantissa = product << (-shift_amount)
        else:
            shift_amount = total_bits - mant_bits_result
            if shift_amount >= 0:
                normalized_mantissa = product >> shift_amount
            else:
                normalized_mantissa = product << (-shift_amount)
        
        result_mantissa = normalized_mantissa - (1 << mant_bits_result)
        
        result_exp_biased = result_exp_unbiased + bias_result
        
        max_exp = (2 ** exp_bits_result) - 1
        if result_exp_biased >= max_exp:
            return CustomFloat((sign_result, max_exp, 0, prec))
        elif result_exp_biased <= 0:
            return CustomFloat((sign_result, 0, 0, prec))
        
        return CustomFloat((sign_result, result_exp_biased, result_mantissa, prec))