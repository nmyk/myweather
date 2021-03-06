import main as seanweather


def test_parse_temps():
    weather_data = [{'temp': '83', 'temp_c': '28'},
                    {'temp': '81', 'temp_c': '27'},
                    {'temp': '85', 'temp_c': '29'}]
    weather_data *= 10
    # The below two data points are outside the default 24-hour period, so they
    # should not be included in the max/min calculation
    weather_data.append({'temp': '100', 'temp_c': '100'})
    weather_data.append({'temp': '0', 'temp_c': '0'})

    f_current, f_max, f_min = seanweather.parse_temps(weather_data)
    assert f_current == 83
    assert f_max == 85
    assert f_min == 81
    c_current, c_max, c_min = seanweather.parse_temps(weather_data, units='C')
    assert c_current == 28
    assert c_max == 29
    assert c_min == 27
