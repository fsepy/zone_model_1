if __name__ == "__main__":
    from zone_model_1 import main_model_as_function

    (
        output_time_arr,
        output_gas_temp_arr,
        output_char_depth_arr,
        output_charring_rate_arr,
        output_MLR_arr,
        output_HRR_wood_arr,
        output_HRR_total_arr,
        output_HRR_ext_arr,
        HRR_time_arr,
        HRR_hrr_arr,
    ) = main_model_as_function()

    import matplotlib.pyplot as plt

    plt.style.use('seaborn-v0_8-whitegrid')
    fig, ax1 = plt.subplots()
    ax1.plot(output_time_arr, output_gas_temp_arr, label='Gas')
    ax1.set_ylabel('Temperature [$^o$C]')
    ax1.minorticks_on()
    fig.tight_layout()

    fig, ax2 = plt.subplots()
    ax2.plot(output_time_arr, output_char_depth_arr, label='Char')
    ax2.set_xlabel('Time [min]')
    ax2.set_ylabel('Char depth [mm]')
    fig.tight_layout()

    fig, ax3 = plt.subplots()
    ax3.plot(output_time_arr, output_charring_rate_arr, label='Char')
    ax3.set_xlabel('Time [min]')
    ax3.set_ylabel('Charring rate [mm/min]')
    fig.tight_layout()

    fig, ax4 = plt.subplots()
    ax4.plot(output_time_arr, output_MLR_arr, label='Char')
    ax4.set_xlabel('Time [min]')
    ax4.set_ylabel('MLR [kg/m$^2$/s]')
    fig.tight_layout()

    fig, ax5 = plt.subplots()
    ax5.plot(output_time_arr, output_HRR_wood_arr, label='wood')
    ax5.plot(HRR_time_arr, HRR_hrr_arr, label='contents')
    ax5.plot(output_time_arr, output_HRR_total_arr, label='total internal')
    ax5.plot(output_time_arr, output_HRR_ext_arr, label='total external')
    ax5.set_xlabel('Time [min]')
    ax5.set_ylabel('HRR [W]')
    ax5.legend().set_visible(True)
    fig.tight_layout()

    plt.show()
