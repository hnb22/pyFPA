import math
from core.float import CustomFloat

class BasicMultiplication:

    @staticmethod
    def multiply(a: CustomFloat, b: CustomFloat, prec: int) -> CustomFloat:
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

        result_sign = sign_a ^ sign_b # XOR for sign multiplication
        
        # Get bit allocations for both operands
        _, exp_bits_a, mant_bits_a = a.get_bit_allocation()
        _, exp_bits_b, mant_bits_b = b.get_bit_allocation()

        # Calculate bit allocation for result
        exp_bits_result = max(8, int(math.log2(prec)) + 2)
        mant_bits_result = prec - exp_bits_result - 1

        # Calculate biases
        bias_a = (2 ** (exp_bits_a - 1)) - 1
        bias_b = (2 ** (exp_bits_b - 1)) - 1
        bias_result = (2 ** (exp_bits_result - 1)) - 1

        # Convert to unbiased exponents and add them
        unbiased_exp_a = exp_a - bias_a
        unbiased_exp_b = exp_b - bias_b
        result_exp_unbiased = unbiased_exp_a + unbiased_exp_b

        # Multiply mantissas (both in 1.xxxxx format)
        full_mant_a = (1 << mant_bits_a) + mant_a  
        full_mant_b = (1 << mant_bits_b) + mant_b  

        # Multiply: result represents (1.x × 1.y) × 2^(mant_bits_a + mant_bits_b)  
        product = full_mant_a * full_mant_b
        total_bits = mant_bits_a + mant_bits_b
        
        # Normalize the product to 1.xxxxx format
        if product >= (1 << (total_bits + 1)):
            # Product >= 2.0, normalize by shifting right and increment exponent
            result_exp_unbiased += 1
            # Calculate shift amount, ensuring it's not negative
            shift_amount = total_bits + 1 - mant_bits_result
            if shift_amount >= 0:
                normalized_mantissa = product >> shift_amount
            else:
                # Target precision is higher, shift left instead
                normalized_mantissa = product << (-shift_amount)
        else:
            # Product < 2.0, just scale to target precision
            shift_amount = total_bits - mant_bits_result
            if shift_amount >= 0:
                # Normal case: shift right to reduce precision
                normalized_mantissa = product >> shift_amount
            else:
                # Target precision is higher than source, shift left to pad with zeros
                normalized_mantissa = product << (-shift_amount)
        
        # Extract fractional part (remove implicit leading 1)
        result_mantissa = normalized_mantissa - (1 << mant_bits_result)
        
        # Apply bias to result exponent
        result_exp_biased = result_exp_unbiased + bias_result
        
        # Handle overflow/underflow
        max_exp = (2 ** exp_bits_result) - 1
        if result_exp_biased >= max_exp:
            # Overflow to infinity
            return CustomFloat((result_sign, max_exp, 0, prec))
        elif result_exp_biased <= 0:
            # Underflow to zero
            return CustomFloat((result_sign, 0, 0, prec))

        return CustomFloat((result_sign, result_exp_biased, result_mantissa, prec))

# Testing
if __name__ == "__main__":
    # Test: High precision
    j = CustomFloat(1.123456789, precision=128)
    k = CustomFloat(2.987654321, precision=128)
    print("Value j tuple:", j.tuple)
    print("Value k tuple:", k.tuple)
    result = BasicMultiplication.multiply(j, k, prec = 1000)
    expected = 1.123456789 * 2.987654321
    print(f"1.123456789 × 2.987654321 = {result} (expected: {expected})")

    # Test: Low precision
    j = CustomFloat(1.1234, precision=128)
    k = CustomFloat(2.987, precision=128)
    print("Value j tuple:", j.tuple)
    print("Value k tuple:", k.tuple)
    result = BasicMultiplication.multiply(j, k, prec = 64)
    expected = 1.1234 * 2.987
    print(f"1.123456789 × 2.987654321 = {result} (expected: {expected})")