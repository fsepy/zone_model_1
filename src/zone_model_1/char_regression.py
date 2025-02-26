# 26/02/25
# Danny Hopkin
# Functions for computing HRR from char regression during the decay phase

def char_reg_HRR(char_density, regression_rate, char_HoC):

    char_reg_RHR = regression_rate * char_density * char_HoC

    return char_reg_RHR

def char_density(char_thick):
    char_rho = 230 / (char_thick ** 0.5)
    return char_rho

if __name__ == "__main__":

    char_density = 40 #kg/m3
    char_HoC = 32 # MJ/kg
    regression_rate = 1 #mm/min

    HRR = char_reg_HRR(char_density, regression_rate/(60*1000), char_HoC)

    print(HRR * 1000, ' kW/sq.m')