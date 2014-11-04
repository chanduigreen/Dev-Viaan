# Converts fixed point number with 4 digits and decimal placement to floating point number.
# Values can be between 0 to 9999 with resolution going into the hundredths.
# a decimal of 1 means tenths and 2 means hundredths. 
# Inputs: a list containing 4 digits with most significant digit first and decimal place last
# Outputs: a single floating point number
def ConvertDecToPreset(digits):
   print "getting here 1"
   for i in range(0, len(digits)):
      digits[i] = float(digits[i])
   print "getting here 2"
   value = float((digits[0]*1000) + (digits[1]*100) + (digits[2]*10) + (digits[3]))
   if digits[4] == 1:
      value = float(value/10)
   elif digits[4] == 2:
      value = float(value/100)
   print "getting here 3"
   return value
