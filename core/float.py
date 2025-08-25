"""
Custom precision floating point representation, and some 
useful methods
"""

from typing import Tuple, Union, Optional
import math

class CustomFloat:
    def __init__(self, value: Union[float, int, str, Tuple[int, int, int, int]] = 0.0, 
                 precision: int = 64):
        if isinstance(value, tuple) and len(value) == 4:
            # Direct tuple initialization: (sign, exponent, mantissa, precision)
            self._value = value
        else:
            # Convert from standard types
            self._value = self._from_value(value, precision)

    def _from_value(self, value: Union[float, int, str], precision: int) -> Tuple[int, int, int, int]:
        """Convert standard numeric types to tuple representation for arbitrary precision."""
        if isinstance(value, str):
            value = float(value)
        elif isinstance(value, int):
            value = float(value)
        
        # Handle zero case
        if value == 0.0:
            return (0, 0, 0, precision)
        
        # For arbitrary precision, we allocate bits more flexibly
        # Use logarithmic allocation: more precision = more mantissa bits
        exponent_bits = max(8, int(math.log2(precision)) + 2)  # Dynamic exponent allocation
        mantissa_bits = precision - exponent_bits - 1  # Reserve 1 bit for sign
        
        # Handle special cases (inf, nan) 
        if math.isinf(value):
            max_exp = (2 ** exponent_bits) - 1
            return (0 if value > 0 else 1, max_exp, 0, precision)
        
        if math.isnan(value):
            max_exp = (2 ** exponent_bits) - 1
            return (0, max_exp, 1, precision)
        
        # Extract sign and work with absolute value
        sign = 0 if value >= 0 else 1
        abs_value = abs(value)
        
        # Find the exponent using floor of log2
        exponent = int(math.floor(math.log2(abs_value)))
        
        # Calculate the mantissa (fractional part after normalization)
        # For arbitrary precision, we want exact representation
        mantissa_float = abs_value / (2.0 ** exponent) - 1.0
        
        # Convert mantissa to integer representation with full precision
        mantissa = int(mantissa_float * (2 ** mantissa_bits))
        
        # Apply bias to exponent for storage
        # Use symmetric bias for arbitrary precision
        exponent_bias = (2 ** (exponent_bits - 1)) - 1
        biased_exponent = exponent + exponent_bias
        
        # Handle exponent overflow/underflow
        max_exp = (2 ** exponent_bits) - 2  # Reserve max value for inf/nan
        if biased_exponent >= max_exp:
            # Overflow to infinity
            return (sign, max_exp + 1, 0, precision)
        elif biased_exponent <= 0:
            # Underflow to zero (could implement subnormal numbers here)
            return (sign, 0, 0, precision)
        
        return (sign, biased_exponent, mantissa, precision)
    
    @property
    def tuple(self) -> Tuple[int, int, int, int]:
        """Return the tuple representation (sign, exponent, mantissa, precision)."""
        return self._value
    
    @property 
    def sign(self) -> int:
        """Return the sign bit (0 for positive, 1 for negative)."""
        return self._value[0]
    
    @property
    def exponent(self) -> int:
        """Return the biased exponent."""
        return self._value[1]
    
    @property 
    def mantissa(self) -> int:
        """Return the mantissa as integer."""
        return self._value[2]
    
    @property
    def precision_bits(self) -> int:
        """Return the precision in bits."""
        return self._value[3]
    
    def to_float(self) -> float:
        """Convert back to standard Python float (limited by Python's precision)."""
        sign, exp, mantissa, precision = self._value
        
        if exp == 0 and mantissa == 0:
            return 0.0
        
        # Calculate bit allocation (same as in _from_value)
        exponent_bits = max(8, int(math.log2(precision)) + 2)
        mantissa_bits = precision - exponent_bits - 1
        
        # Handle special values
        max_exp = (2 ** exponent_bits) - 1
        if exp == max_exp:
            if mantissa == 0:
                return float('inf') if sign == 0 else float('-inf')
            else:
                return float('nan')
        
        # Reconstruct the value
        exponent_bias = (2 ** (exponent_bits - 1)) - 1
        actual_exponent = exp - exponent_bias
        
        mantissa_value = 1.0 + (mantissa / (2 ** mantissa_bits))
        
        result = mantissa_value * (2.0 ** actual_exponent)
        return -result if sign == 1 else result
    
    def __str__(self) -> str:
        """String representation showing the float value."""
        return str(self.to_float())
    
    def __repr__(self) -> str:
        """Detailed representation showing tuple format."""
        return f"CustomFloat(sign={self.sign}, exp={self.exponent}, " \
               f"mantissa={self.mantissa}, precision={self.precision_bits})"
    
    def get_bit_allocation(self) -> Tuple[int, int, int]:
        """Return the bit allocation (sign_bits, exponent_bits, mantissa_bits)."""
        precision = self.precision_bits
        exponent_bits = max(8, int(math.log2(precision)) + 2)
        mantissa_bits = precision - exponent_bits - 1
        return (1, exponent_bits, mantissa_bits)
    
    def to_binary_string(self) -> str:
        """Return binary representation for debugging."""
        sign_bits, exp_bits, mant_bits = self.get_bit_allocation()
        
        sign_str = f"{self.sign:01b}"
        exp_str = f"{self.exponent:0{exp_bits}b}"
        mant_str = f"{self.mantissa:0{mant_bits}b}"
        
        return f"{sign_str}|{exp_str}|{mant_str}"
    
    def effective_precision(self) -> int:
        """Calculate the effective decimal precision of this representation."""
        _, _, mantissa_bits = self.get_bit_allocation()
        # Each bit provides log10(2) ≈ 0.301 decimal digits of precision
        return int(mantissa_bits * math.log10(2))


#Testing
cf = CustomFloat(12.75, precision=128)
print(cf.tuple)
cf2 = CustomFloat((0, 258, 197307280624323449884158860510363648, 128))
print(cf2)
    