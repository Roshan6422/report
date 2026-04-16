"""
Police Station → S/DIG Province and DIG District mapping.
Complete list of all Sri Lanka Police stations (~300+ major stations).
Used by report_formatter.py and translator_pipeline.py to group incidents by province.
"""

STATION_MAP = {
    # ===== WESTERN PROVINCE =====
    # -- DIG Colombo District / Colombo Central --
    "Colombo": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Fort": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Pettah": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Dam Street": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Maradana": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Slave Island": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Maligawatta": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Keselwatta": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Wolfendhal": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Borella": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Cinnamon Gardens": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Kaduwela": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Kolonnawa": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Battaramulla": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Welikada": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Mirihana": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Thalangama": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Colombo (C) Div."},
    "Wellampitiya": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Nugegoda Div."},
    "Gothatuwa": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Nugegoda Div."},
    "Meepe": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo District", "div": "Nugegoda Div."},
    # -- DIG Colombo North --
    "Kotahena": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo North", "div": "Colombo (N) Div."},
    "Madampitiya": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo North", "div": "Colombo (N) Div."},
    "Modara": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo North", "div": "Colombo (N) Div."},
    "Mulleriyawa": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo North", "div": "Colombo (N) Div."},
    "Grandpass": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo North", "div": "Colombo (N) Div."},
    "Mattakkuliya": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo North", "div": "Colombo (N) Div."},
    "Bloemendhal": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo North", "div": "Colombo (N) Div."},
    "Dematagoda": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo North", "div": "Colombo (N) Div."},
    # -- DIG Colombo South --
    "Bambalapitiya": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo South", "div": "Colombo (S) Div."},
    "Wellawatte": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo South", "div": "Colombo (S) Div."},
    "Narahenpita": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo South", "div": "Colombo (S) Div."},
    "Kirulapone": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo South", "div": "Colombo (S) Div."},
    "Kollupitiya": {"province": "WESTERN PROVINCE", "dig": "DIG Colombo South", "div": "Colombo (S) Div."},
    # -- DIG Mt. Lavinia District --
    "Mount Lavinia": {"province": "WESTERN PROVINCE", "dig": "DIG Mt. Lavinia District", "div": "Mt. Lavinia Div."},
    "Dehiwala": {"province": "WESTERN PROVINCE", "dig": "DIG Mt. Lavinia District", "div": "Mt. Lavinia Div."},
    "Galkissa": {"province": "WESTERN PROVINCE", "dig": "DIG Mt. Lavinia District", "div": "Mt. Lavinia Div."},
    "Boralesgamuwa": {"province": "WESTERN PROVINCE", "dig": "DIG Mt. Lavinia District", "div": "Mt. Lavinia Div."},
    "Moratuwa": {"province": "WESTERN PROVINCE", "dig": "DIG Mt. Lavinia District", "div": "Mt. Lavinia Div."},
    "Ratmalana": {"province": "WESTERN PROVINCE", "dig": "DIG Mt. Lavinia District", "div": "Mt. Lavinia Div."},
    # -- DIG Kelaniya District --
    "Kelaniya": {"province": "WESTERN PROVINCE", "dig": "DIG Kelaniya District", "div": "Kelaniya Div."},
    "Sapugaskanda": {"province": "WESTERN PROVINCE", "dig": "DIG Kelaniya District", "div": "Kelaniya Div."},
    "Kadawatha": {"province": "WESTERN PROVINCE", "dig": "DIG Kelaniya District", "div": "Kelaniya Div."},
    "Kiribathgoda": {"province": "WESTERN PROVINCE", "dig": "DIG Kelaniya District", "div": "Kelaniya Div."},
    "Ragama": {"province": "WESTERN PROVINCE", "dig": "DIG Kelaniya District", "div": "Kelaniya Div."},
    "Enderamulla": {"province": "WESTERN PROVINCE", "dig": "DIG Kelaniya District", "div": "Kelaniya Div."},
    "Biyagama": {"province": "WESTERN PROVINCE", "dig": "DIG Kelaniya District", "div": "Kelaniya Div."},
    # -- DIG Homagama District --
    "Homagama": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    "Nawagamuwa": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    "Meegoda": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    "Hanwella": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    "Nugegoda": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    "Maharagama": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    "Kottawa": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    "Athurugiriya": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    "Padukka": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    "Kosgama": {"province": "WESTERN PROVINCE", "dig": "DIG Homagama District", "div": "Homagama Div."},
    # -- DIG Panadura District --
    "Panadura": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Piliyandala": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Ingiriya": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Hirana": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Bandaragama": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Horana": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Millaniya": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Morogahahena": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Moronthuduwa": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Panadura North": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Panadura South": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Pinwatta": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Wadduwa": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Anguruwatota": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Kalutara": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Matugama": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Panadura Div."},
    "Aluthgama": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Baduraliya": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Beruwala": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Bulathsinhala": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Dodangoda": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Kalutara North": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Kalutara South": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Mattegoda": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Meegahathenna": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Payagala": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Thebuwana": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Thiniyawala": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    "Welipanna": {"province": "WESTERN PROVINCE", "dig": "DIG Panadura District", "div": "Kalutara Div."},
    # -- DIG Negombo District --
    "Negombo": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Katana": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Wattala": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Ja-Ela": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Mahabage": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Seeduwa": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Katunayaka": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Kochchikade": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Dungalpitiya": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Kotadeniyawa": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Pamunugama": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    "Raddolugama": {"province": "WESTERN PROVINCE", "dig": "DIG Negombo District", "div": "Negombo Div."},
    # -- DIG Gampaha District --
    "Gampaha": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Nalla": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Minuwangoda": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Karagampitiya": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Divulapitiya": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Dompe": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Nittambuwa": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Veyangoda": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Mirigama": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Pugoda": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Attanagalla": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},
    "Peliyagoda": {"province": "WESTERN PROVINCE", "dig": "DIG Gampaha District", "div": "Gampaha Div."},

    # ===== SOUTHERN PROVINCE =====
    # -- DIG Galle District --
    "Galle": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Hikkaduwa": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Ambalangoda": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Ahangama": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Udugama": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Galwaduwatta": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Imaduwa": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Habaraduwa": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Nagoda": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Hiniduma": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Neluwa": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Akmeemana": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Galle Harbour": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Poddala": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Rathgama": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Unawatuna": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Wanduramba": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Yakkalamulla": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Benthota": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Karandeniya": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Kosgoda": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    "Pitigala": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Galle Div."},
    # -- DIG Galle / Elpitiya Div --
    "Baddegama": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Elpitiya Div."},
    "Elpitiya": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Elpitiya Div."},
    "Gonapinuwala": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Elpitiya Div."},
    "Uragasmanhandiya": {"province": "SOUTHERN PROVINCE", "dig": "DIG Galle District", "div": "Elpitiya Div."},
    # -- DIG Matara District --
    "Matara": {"province": "SOUTHERN PROVINCE", "dig": "DIG Matara District", "div": "Matara Div."},
    "Hakmana": {"province": "SOUTHERN PROVINCE", "dig": "DIG Matara District", "div": "Matara Div."},
    "Maliwabada": {"province": "SOUTHERN PROVINCE", "dig": "DIG Matara District", "div": "Matara Div."},
    "Weligama": {"province": "SOUTHERN PROVINCE", "dig": "DIG Matara District", "div": "Matara Div."},
    "Deniyaya": {"province": "SOUTHERN PROVINCE", "dig": "DIG Matara District", "div": "Matara Div."},
    "Akuressa": {"province": "SOUTHERN PROVINCE", "dig": "DIG Matara District", "div": "Matara Div."},
    "Devinuwara": {"province": "SOUTHERN PROVINCE", "dig": "DIG Matara District", "div": "Matara Div."},
    "Dikwella": {"province": "SOUTHERN PROVINCE", "dig": "DIG Matara District", "div": "Matara Div."},
    "Kamburupitiya": {"province": "SOUTHERN PROVINCE", "dig": "DIG Matara District", "div": "Matara Div."},
    # -- DIG Hambantota District --
    "Hambantota": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Tangalle": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Beliatta": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Thissamaharamaya": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Tissamaharama": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Kirinda": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Kataragama": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Ambalantota": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Walasmulla": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Weeraketiya": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Middeniya": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},
    "Sooriyawewa": {"province": "SOUTHERN PROVINCE", "dig": "DIG Hambantota District", "div": "Hambantota Div."},

    # ===== CENTRAL PROVINCE =====
    # -- DIG Kandy District --
    "Kandy": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Mahanuwara": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Pallekele": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Peradeniya": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Hatharaliyadda": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Gampola": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Nawalapitiya": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Kadugannawa": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Katugastota": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Galagedara": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Theldeniya": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Wattegama": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Alawathugoda": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Panwila": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Hasalaka": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Pussellawa": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    # -- DIG Matale District --
    "Matale": {"province": "CENTRAL PROVINCE", "dig": "DIG Matale District", "div": "Matale Div."},
    "Dambulla": {"province": "CENTRAL PROVINCE", "dig": "DIG Matale District", "div": "Matale Div."},
    "Galewela": {"province": "CENTRAL PROVINCE", "dig": "DIG Matale District", "div": "Matale Div."},
    "Rattota": {"province": "CENTRAL PROVINCE", "dig": "DIG Matale District", "div": "Matale Div."},
    "Naula": {"province": "CENTRAL PROVINCE", "dig": "DIG Matale District", "div": "Matale Div."},
    "Sigiriya": {"province": "CENTRAL PROVINCE", "dig": "DIG Matale District", "div": "Matale Div."},
    "Wilgamuwa": {"province": "CENTRAL PROVINCE", "dig": "DIG Matale District", "div": "Matale Div."},
    # -- DIG Nuwara Eliya District --
    "Nuwara Eliya": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Hatton": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Hatton Div."},
    "Lipu": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Thalawakele": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Kothmale": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Agarapathana": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Walapane": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Dayagama": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Dimbulapathana": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Kandapola": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Mandaram Nuwara": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Maturata": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Nanuoya": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Punduloya": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Ragala": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Theripaha": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    "Udupussellawa": {"province": "CENTRAL PROVINCE", "dig": "DIG Nuwara Eliya District", "div": "Nuwara Eliya Div."},
    # -- DIG Kandy District --
    "Ankumbura": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Dalada Maligawa": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Daulagala": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Hanguranketha": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Poojapitiya": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Thalathuoya": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    "Welambada": {"province": "CENTRAL PROVINCE", "dig": "DIG Kandy District", "div": "Kandy Div."},
    # -- DIG Hatton District --
    "Bogawanthalawa": {"province": "CENTRAL PROVINCE", "dig": "DIG Hatton District", "div": "Hatton Div."},
    "Ginigathhena": {"province": "CENTRAL PROVINCE", "dig": "DIG Hatton District", "div": "Hatton Div."},
    "Maskeliya": {"province": "CENTRAL PROVINCE", "dig": "DIG Hatton District", "div": "Hatton Div."},
    "Nallathanni": {"province": "CENTRAL PROVINCE", "dig": "DIG Hatton District", "div": "Hatton Div."},
    "Nortonbridge": {"province": "CENTRAL PROVINCE", "dig": "DIG Hatton District", "div": "Hatton Div."},
    "Norwood": {"province": "CENTRAL PROVINCE", "dig": "DIG Hatton District", "div": "Hatton Div."},
    "Watawala": {"province": "CENTRAL PROVINCE", "dig": "DIG Hatton District", "div": "Hatton Div."},

    # ===== NORTH WESTERN PROVINCE =====
    # -- DIG Kurunegala District --
    "Kurunegala": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Mawathagama": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Wariyapola": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Gokarella": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Weerambugedara": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Maduragoda": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Polgahawela": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Alawwa": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Rideegama": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Wellawa": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    "Nikaweratiya": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kurunegala Div."},
    # -- DIG Kurunegala / Kuliyapitiya Div --
    "Kuliyapitiya": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kuliyapitiya Div."},
    "Bingiriya": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kuliyapitiya Div."},
    "Narammala": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kuliyapitiya Div."},
    "Hettipola": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kuliyapitiya Div."},
    "Pannala": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kuliyapitiya Div."},
    "Giriulla": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kuliyapitiya Div."},
    "Dummalasooriya": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Kurunegala District", "div": "Kuliyapitiya Div."},
    # -- DIG Puttalam District --
    "Puttalam": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Anamaduwa": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Chilaw": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Wennappuwa": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Madampe": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Norochcholai": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Kalpitiya": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Marawila": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Dankotuwa": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Mundel": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},
    "Thelukkuma": {"province": "NORTH WESTERN PROVINCE", "dig": "DIG Puttalam District", "div": "Puttalam Div."},

    # ===== SABARAGAMUWA PROVINCE =====
    # -- DIG Ratnapura District --
    "Ratnapura": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Ratnapura Div."},
    "Embilipitiya": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Embilipitiya Div."},
    "Ayagama": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Ratnapura Div."},
    "Rakwana": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Ratnapura Div."},
    "Bangoda": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Ratnapura Div."},
    "Balangoda": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Ratnapura Div."},
    "Eheliyagoda": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Ratnapura Div."},
    "Kahawatta": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Ratnapura Div."},
    "Opanayaka": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Ratnapura Div."},
    "Weligepola": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Ratnapura District", "div": "Ratnapura Div."},
    # -- DIG Kegalle District --
    "Kegalle": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Kegalle District", "div": "Kegalle Div."},
    "Ruwanwella": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Kegalle District", "div": "Seethawakapura Div."},
    "Dehiowita": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Kegalle District", "div": "Seethawakapura Div."},
    "Warakapola": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Kegalle District", "div": "Kegalle Div."},
    "Mawanella": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Kegalle District", "div": "Kegalle Div."},
    "Rambukkana": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Kegalle District", "div": "Kegalle Div."},
    "Aranayaka": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Kegalle District", "div": "Kegalle Div."},
    "Deraniyagala": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Kegalle District", "div": "Kegalle Div."},
    "Yatiyanthota": {"province": "SABARAGAMUWA PROVINCE", "dig": "DIG Kegalle District", "div": "Kegalle Div."},

    # ===== NORTH CENTRAL PROVINCE =====
    # -- DIG Anuradhapura District --
    "Anuradhapura": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Thambuththegama": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Thambuththegama Div."},
    "Eppawala": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Thambuththegama Div."},
    "Rajanganaya": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Kekirawa": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Kebithigollewa": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Mihintale": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Medawachchiya": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Nochchiyagama": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Talawa": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Galenbidunuwewa": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Galkiriyagama": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Galnewa": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Hidogama": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Moragoda": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Padaviya": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Parasangaswewa": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Thanthirimalaya": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Thirappone": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    "Udamaluwa": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Anuradhapura District", "div": "Anuradhapura Div."},
    # -- DIG Polonnaruwa District --
    "Polonnaruwa": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Polonnaruwa District", "div": "Polonnaruwa Div."},
    "Bakamuna": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Polonnaruwa District", "div": "Polonnaruwa Div."},
    "Hingurakgoda": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Polonnaruwa District", "div": "Polonnaruwa Div."},
    "Medirigiriya": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Polonnaruwa District", "div": "Polonnaruwa Div."},
    "Welikanda": {"province": "NORTH CENTRAL PROVINCE", "dig": "DIG Polonnaruwa District", "div": "Polonnaruwa Div."},

    # ===== EASTERN PROVINCE =====
    # -- DIG Trincomalee District --
    "Trincomalee": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Trincomalee Div."},
    "Kinniya": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Trincomalee Div."},
    "Kanthale": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Trincomalee Div."},
    "Agbopura": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Kantale Div."},
    "Gomarankadawala": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Kantale Div."},
    "Morawewa": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Kantale Div."},
    "Serunuwara": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Kantale Div."},
    "Suriyapura": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Kantale Div."},
    "Thoppur": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Kantale Div."},
    "Uppuveli": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Kantale Div."},
    "Muthur": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Trincomalee Div."},
    "Seruwila": {"province": "EASTERN PROVINCE", "dig": "DIG Trincomalee District", "div": "Trincomalee Div."},
    # -- DIG Batticaloa District --
    "Batticaloa": {"province": "EASTERN PROVINCE", "dig": "DIG Batticaloa District", "div": "Batticaloa Div."},
    "Eravur": {"province": "EASTERN PROVINCE", "dig": "DIG Batticaloa District", "div": "Batticaloa Div."},
    "Kalkuda": {"province": "EASTERN PROVINCE", "dig": "DIG Batticaloa District", "div": "Batticaloa Div."},
    # -- DIG Ampara District --
    "Ampara": {"province": "EASTERN PROVINCE", "dig": "DIG Ampara District", "div": "Ampara Div."},
    "Samanthurai": {"province": "EASTERN PROVINCE", "dig": "DIG Ampara District", "div": "Ampara Div."},
    "Iginiyagala": {"province": "EASTERN PROVINCE", "dig": "DIG Ampara District", "div": "Ampara Div."},
    "Kalmunai": {"province": "EASTERN PROVINCE", "dig": "DIG Ampara District", "div": "Ampara Div."},
    "Akkaraipattu": {"province": "EASTERN PROVINCE", "dig": "DIG Ampara District", "div": "Ampara Div."},
    "Pottuvil": {"province": "EASTERN PROVINCE", "dig": "DIG Ampara District", "div": "Ampara Div."},
    "Uhana": {"province": "EASTERN PROVINCE", "dig": "DIG Ampara District", "div": "Ampara Div."},

    # ===== NORTHERN PROVINCE =====
    # -- DIG Jaffna District --
    "Jaffna": {"province": "NORTHERN PROVINCE", "dig": "DIG Jaffna District", "div": "Jaffna Div."},
    "Chavakachcheri": {"province": "NORTHERN PROVINCE", "dig": "DIG Jaffna District", "div": "Jaffna Div."},
    "Chankanai": {"province": "NORTHERN PROVINCE", "dig": "DIG Jaffna District", "div": "Jaffna Div."},
    "Point Pedro": {"province": "NORTHERN PROVINCE", "dig": "DIG Jaffna District", "div": "Jaffna Div."},
    "Kopay": {"province": "NORTHERN PROVINCE", "dig": "DIG Jaffna District", "div": "Jaffna Div."},
    "Chunnakam": {"province": "NORTHERN PROVINCE", "dig": "DIG Jaffna District", "div": "Jaffna Div."},
    "Nelliady": {"province": "NORTHERN PROVINCE", "dig": "DIG Jaffna District", "div": "Jaffna Div."},
    "Vaddukoddai": {"province": "NORTHERN PROVINCE", "dig": "DIG Jaffna District", "div": "Jaffna Div."},
    "Kayts": {"province": "NORTHERN PROVINCE", "dig": "DIG Jaffna District", "div": "Jaffna Div."},
    # -- Other Northern Districts --
    "Kilinochchi": {"province": "NORTHERN PROVINCE", "dig": "DIG Kilinochchi District", "div": "Kilinochchi Div."},
    "Mannar": {"province": "NORTHERN PROVINCE", "dig": "DIG Mannar District", "div": "Mannar Div."},
    "Mullaitivu": {"province": "NORTHERN PROVINCE", "dig": "DIG Mullaitivu District", "div": "Mullaitivu Div."},
    "Pudukudirippu": {"province": "NORTHERN PROVINCE", "dig": "DIG Mullaitivu District", "div": "Mullaitivu Div."},
    "Vavuniya": {"province": "NORTHERN PROVINCE", "dig": "DIG Vavuniya District", "div": "Vavuniya Div."},
    "Akkarayamkulam": {"province": "NORTHERN PROVINCE", "dig": "DIG Kilinochchi District", "div": "Kilinochchi Div."},
    "Dharmapuram": {"province": "NORTHERN PROVINCE", "dig": "DIG Kilinochchi District", "div": "Kilinochchi Div."},
    "Mulankavil": {"province": "NORTHERN PROVINCE", "dig": "DIG Kilinochchi District", "div": "Kilinochchi Div."},
    "Nachchikudha": {"province": "NORTHERN PROVINCE", "dig": "DIG Kilinochchi District", "div": "Kilinochchi Div."},
    "Pallai": {"province": "NORTHERN PROVINCE", "dig": "DIG Kilinochchi District", "div": "Kilinochchi Div."},
    "Pooneryn": {"province": "NORTHERN PROVINCE", "dig": "DIG Kilinochchi District", "div": "Kilinochchi Div."},

    # ===== UVA PROVINCE =====
    # -- DIG Badulla District --
    "Badulla": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Badulla Div."},
    "Mahiyangana": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Badulla Div."},
    "Welimada": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Badulla Div."},
    "Passara": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Badulla Div."},
    "Haliela": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Badulla Div."},
    "Giradurukotte": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Badulla Div."},
    "Kandaketiya": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Badulla Div."},
    "Horokkopotana": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Kebithigollewa Div."},
    "Kambukkan": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Badulla Div."},
    # -- DIG Badulla / Bandarawela Div --
    "Bandarawela": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Bandarawela Div."},
    "Haputale": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Bandarawela Div."},
    "Ella": {"province": "UVA PROVINCE", "dig": "DIG Badulla District", "div": "Bandarawela Div."},
    # -- DIG Monaragala District --
    "Monaragala": {"province": "UVA PROVINCE", "dig": "DIG Monaragala District", "div": "Monaragala Div."},
    "Bibile": {"province": "UVA PROVINCE", "dig": "DIG Monaragala District", "div": "Monaragala Div."},
    "Wellawaya": {"province": "UVA PROVINCE", "dig": "DIG Monaragala District", "div": "Monaragala Div."},
    "Kahataduwa": {"province": "UVA PROVINCE", "dig": "DIG Monaragala District", "div": "Monaragala Div."},
    "Buttala": {"province": "UVA PROVINCE", "dig": "DIG Monaragala District", "div": "Monaragala Div."},

    # ===== SPECIAL UNITS =====
    "CDB": {"province": "SPECIAL", "dig": "S/DIG CRIME", "div": "CDB"},
    "STF": {"province": "SPECIAL", "dig": "S/DIG CRIME", "div": "STF"},
    "DCDB": {"province": "SPECIAL", "dig": "S/DIG CRIME", "div": "CDB"},
    "Police Narcotics Bureau": {"province": "SPECIAL", "dig": "DIG PNB", "div": "Dir. PNB"},
    "Criminal Investigation Department": {"province": "SPECIAL", "dig": "S/DIG CRIME", "div": "CID"},
    "CCD": {"province": "SPECIAL", "dig": "S/DIG CRIME", "div": "CCD"},
}

# Sinhala station name → English mapping (comprehensive)
SINHALA_TO_ENGLISH = {
    # Western Province
    "කොළඹ": "Colombo", "කොටුව": "Fort", "පිට කොටුව": "Pettah",
    "මරදාන": "Maradana", "බොරැල්ල": "Borella",
    "කොත්තේන": "Kotahena", "මාදම්පිටිය": "Madampitiya",
    "මුල්ලෙරියාව": "Mulleriyawa", "බම්බලපිටිය": "Bambalapitiya",
    "වැල්ලවත්ත": "Wellawatte", "නාරාහේන්පිට": "Narahenpita",
    "දෙහිවල": "Dehiwala", "ගල්කිස්ස": "Galkissa",
    "බොරලැස්ගමුව": "Boralesgamuwa", "මොරටුව": "Moratuwa",
    "කෑලණිය": "Kelaniya", "සපුගස්කන්ද": "Sapugaskanda",
    "කඩවත": "Kadawatha", "කිරිබත්ගොඩ": "Kiribathgoda",
    "රාගම": "Ragama", "බියගම": "Biyagama",
    "හෝමාගම": "Homagama", "නවගමුව": "Nawagamuwa",
    "මීගොඩ": "Meegoda", "හන්වැල්ල": "Hanwella",
    "නුගේගොඩ": "Nugegoda", "මහරගම": "Maharagama",
    "කොට්ටාව": "Kottawa", "අතුරුගිරිය": "Athurugiriya",
    "පානදුර": "Panadura", "පිළියන්දල": "Piliyandala",
    "ඉංගිරිය": "Ingiriya", "හිරාන": "Hirana",
    "බණ්ඩාරගම": "Bandaragama", "කළුතර": "Kalutara",
    "බේරුවල": "Beruwala", "මතුගම": "Matugama",
    "මීගමුව": "Negombo", "කටාන": "Katana",
    "වත්තල": "Wattala", "ජා ඇල": "Ja-Ela",
    "මහබාගෙ": "Mahabage", "මී ගමුව": "Negombo",
    "ගම්පහ": "Gampaha", "නාල්ල": "Nalla",
    "මිනුවන්ගොඩ": "Minuwangoda", "කරගම්පිටිය": "Karagampitiya",
    "දිවුලපිටිය": "Divulapitiya", "කඩුවෙල": "Kaduwela",
    "කොළොන්නාව": "Kolonnawa", "බත්තරමුල්ල": "Battaramulla",
    "වැලිකඩ": "Welikada", "මිරිහාන": "Mirihana",
    "තලංගම": "Thalangama", "පදුක්ක": "Padukka",
    "කොස්ගම": "Kosgama", "පැළිගොඩ": "Peliyagoda",
    "වෙල්ලම්පිටිය": "Wellampitiya", "ගෝතටුව": "Gothatuwa", "මීපේ": "Meepe",
    "හොරණ": "Horana", "මිල්ලනිය": "Millaniya", "මොරගහහේන": "Morogahahena",
    "මොරොන්තුඩුව": "Moronthuduwa", "පානදුර උතුර": "Panadura North",
    "පානදුර දකුණ": "Panadura South", "පින්වත්ත": "Pinwatta",
    "වඩ්ඩුව": "Wadduwa", "අඟුරුවාතොට": "Anguruwatota",
    "දුංගල්පිටිය": "Dungalpitiya", "කොටදෙණියාව": "Kotadeniyawa",
    "පමුණුගම": "Pamunugama", "රද්දොළුගම": "Raddolugama",
    "අලුත්ගම": "Aluthgama", "බදුරලිය": "Baduraliya",
    "බුලත්සිංහල": "Bulathsinhala", "දොඩංගොඩ": "Dodangoda",
    "කළුතර උතුර": "Kalutara North", "කළුතර දකුණ": "Kalutara South",
    "මත්තේගොඩ": "Mattegoda", "මීගහතැන්න": "Meegahathenna",
    "පායගල": "Payagala", "තේබුවන": "Thebuwana",
    "තිනියාවල": "Thiniyawala", "වැලිපැන්න": "Welipanna",
    # Southern Province
    "ගාල්ල": "Galle", "හික්කඩුව": "Hikkaduwa",
    "අම්බලන්ගොඩ": "Ambalangoda", "අහංගම": "Ahangama",
    "උඩුගම": "Udugama", "ඉමදුව": "Imaduwa",
    "බද්දේගම": "Baddegama", "ඇල්පිටිය": "Elpitiya",
    "බෙන්තොට": "Benthota",
    "මාතර": "Matara", "හක්මන": "Hakmana",
    "මාලිවබඩ": "Maliwabada", "මලියවඩ": "Maliwabada",
    "වැලිගම": "Weligama", "දෙනියාය": "Deniyaya",
    "අකුරැස්ස": "Akuressa", "දික්වැල්ල": "Dikwella",
    "කඹුරුපිටිය": "Kamburupitiya",
    "හම්බන්තොට": "Hambantota", "තංගල්ල": "Tangalle",
    "බෙලිඅත්ත": "Beliatta", "තිස්සමහාරාමය": "Thissamaharamaya",
    "කිරිඳ": "Kirinda", "කතරගම": "Kataragama",
    "අම්බලන්තොට": "Ambalantota", "වලස්මුල්ල": "Walasmulla",
    "වීරකැටිය": "Weeraketiya", "සූරියවැව": "Sooriyawewa",
    # Central Province
    "මහනුවර": "Kandy", "පල්ලේකැලේ": "Pallekele",
    "පේරාදෙණිය": "Peradeniya", "හතරලියද්ද": "Hatharaliyadda",
    "ගම්පොල": "Gampola", "නාවලපිටිය": "Nawalapitiya",
    "කඩුගන්නාව": "Kadugannawa", "කටුගස්තොට": "Katugastota",
    "ගලගෙදර": "Galagedara", "වත්තේගම": "Wattegama",
    "අලවතුගොඩ": "Alawathugoda", "පුස්සැල්ලාව": "Pussellawa",
    "මාතලේ": "Matale", "දඹුල්ල": "Dambulla",
    "ගලේවෙල": "Galewela", "රත්තොට": "Rattota",
    "නුවරඑළිය": "Nuwara Eliya", "හැටන්": "Hatton",
    "තලවාකැලේ": "Thalawakele",
    # North Western Province
    "කුරුණෑගල": "Kurunegala", "මාවතගම": "Mawathagama",
    "වාරියපොල": "Wariyapola", "ගොකරැල්ල": "Gokarella",
    "වීරම්බුගෙදර": "Weerambugedara", "මාදුරාගොඩ": "Maduragoda",
    "පොල්ගහවෙල": "Polgahawela", "අලව්ව": "Alawwa",
    "නිකවැරටිය": "Nikaweratiya", "කුලියාපිටිය": "Kuliyapitiya",
    "බිංගිරිය": "Bingiriya", "නාරම්මල": "Narammala",
    "හෙට්ටිපොල": "Hettipola", "දුම්මලසූරිය": "Dummalasooriya",
    "පුත්තලම": "Puttalam", "ආණමඩුව": "Anamaduwa",
    "හලාවත": "Chilaw", "වෙන්නප්පුව": "Wennappuwa",
    "මාදම්පේ": "Madampe", "නොරොච්චෝලේ": "Norochcholai",
    "කල්පිටිය": "Kalpitiya", "මාරවිල": "Marawila",
    "දංකොටුව": "Dankotuwa",
    # Sabaragamuwa Province
    "රත්නපුර": "Ratnapura", "ඇඹිලිපිටිය": "Embilipitiya",
    "අයගම": "Ayagama", "රක්වාන": "Rakwana",
    "බංගොඩ": "Bangoda", "බලංගොඩ": "Balangoda",
    "ඇහැළියගොඩ": "Eheliyagoda", "කහවත්ත": "Kahawatta",
    "කෑගල්ල": "Kegalle", "රුවන්වැල්ල": "Ruwanwella",
    "දෙහිඕවිට": "Dehiowita", "වරකාපොල": "Warakapola",
    "මාවනැල්ල": "Mawanella", "රඹුක්කන": "Rambukkana",
    "අරණායක": "Aranayaka", "දෙරණියගල": "Deraniyagala",
    "යටියන්තොට": "Yatiyanthota",
    # North Central Province
    "අනුරාධපුර": "Anuradhapura", "තඹුත්තේගම": "Thambuththegama",
    "එප්පාවල": "Eppawala", "කැකිරාව": "Kekirawa",
    "කැබිතිගොල්ලෑව": "Kebithigollewa", "මිහින්තලේ": "Mihintale",
    "මැදවච්චිය": "Medawachchiya", "නොච්චියාගම": "Nochchiyagama",
    "පොළොන්නරුව": "Polonnaruwa", "බකමුණ": "Bakamuna",
    "හිඟුරක්ගොඩ": "Hingurakgoda", "මැදිරිගිරිය": "Medirigiriya",
    # Eastern Province
    "ත්‍රිකුණාමලය": "Trincomalee", "කින්නියා": "Kinniya",
    "මුතුර්": "Muthur", "කන්තලේ": "Kanthale",
    "මඩකලපුව": "Batticaloa", "එරාවූර්": "Eravur",
    "අම්පාර": "Ampara", "සමන්තුරේ": "Samanthurai",
    "ඉගිණියාගල": "Iginiyagala", "කල්මුනේ": "Kalmunai",
    "අක්කරෙයිපත්තු": "Akkaraipattu", "පොත්තුවිල්": "Pottuvil",
    # Northern Province
    "යාපනය": "Jaffna", "චාවකච්චේරි": "Chavakachcheri",
    "කිලිනොච්චිය": "Kilinochchi", "මන්නාරම": "Mannar",
    "මුල්ලව්තිවු": "Mullaitivu", "පුදුකුඩිරිප්පු": "Pudukudirippu",
    "පුදුක්කුඩිරිප්පු": "Pudukudirippu", "වව්නියාව": "Vavuniya",
    # Uva Province
    "බදුල්ල": "Badulla", "මහියංගනය": "Mahiyangana",
    "වැලිමඩ": "Welimada", "පස්සර": "Passara",
    "බණ්ඩාරවෙල": "Bandarawela", "හපුතලේ": "Haputale",
    "ඇල්ල": "Ella", "මොනරාගල": "Monaragala",
    "බිබිලේ": "Bibile", "වැල්ලවාය": "Wellawaya",
    "රහතුඩුව": "Kahataduwa", "රහතුඩුල": "Kahataduwa",
    "හොරොක්පොතාන": "Horokkopotana", "කම්බුක්කන": "Kambukkan",
    "බුත්තල": "Buttala",
    # Additional Mappings from police_geo_utils
    "අගලවත්ත": "AGALAWATTA", "අත්ත‍නගල්ල": "ATTANAGALLA", "අඹන්පොළ": "AMBANPOLA",
    "අළුත්ගම": "ALUTHGAMA", "එඹිලිපිටිය": "EMBILIPITIYA", "එල්පිටිය": "ELPITIYA",
    "ඒකල": "EKALA", "කටුනායක": "KATUNAYAKE", "කන්නිය": "KINNIYA", "කල්මුණේ": "KALMUNAI",
    "කිරුළ‍ාපොන": "KIRULAPONE", "කිලිනොච්චි": "KILINOCHCHI", "කුළියාපිටිය": "KULIYAPITIYA",
    "කේකිරාව": "KEKIRAWA", "කේලණිය": "KELANIYA", "කේස්බෑව": "KESBEWA",
    "කොලොන්නාව": "KOLONNAWA", "කොළඹ මහ": "FORT", "ක‍ටාන": "KATANA", "ක‍ළුතර": "KALUTARA",
    "ගනේමුල්ල": "GANEMULLA", "ග‍ැ‍ම්පහ": "GAMPAHA", "චිලාව": "CHILAW", "ජා‍ ඇල": "JA-ELA",
    "ත්‍රිකුණාමල": "TRINCOMALEE", "තිස්සමහාරාම": "TISSAMAHARAMA", "නිට්ටඹුව": "NITTAMBUWA",
    "පන්නිපිටිය": "PANNIPITIYA", "පිළියන්ද‍ල": "PILIYANDALA", "පිළිසස්": "PETTAH",
    "පේලියගොඩ": "PELIYAGODA", "බුළත්සිංහල": "BULATHSINHALA", "මාතුගම": "MATHUGAMA",
    "මාළාබේ": "MALABE", "මූලතිව්": "MULLAITIVU", "මේදවච්චිය": "MEDAWACHCHIYA",
    "රත්මලාන": "RATMALANA", "වව්නියා": "VAVUNIYA", "වේයන්ගොඩ": "VEYANGODA",
    "වේලිගම": "WELIGAMA", "ශ්‍රී ජයවර්ධනපුර": "SRI JAYAWARDENEPURA", "සීගිරිය": "SIGIRIYA",
    "සීදුව": "SEEDUWA", "හාපුතලේ": "HAPUTALE", "හේදල": "HENDALA",
}

# Province display order (matches official IG's Command format)
PROVINCE_ORDER = [
    "SPECIAL",
    "WESTERN PROVINCE",
    "SOUTHERN PROVINCE",
    "CENTRAL PROVINCE",
    "NORTH WESTERN PROVINCE",
    "SABARAGAMUWA PROVINCE",
    "NORTH CENTRAL PROVINCE",
    "EASTERN PROVINCE",
    "NORTHERN PROVINCE",
    "UVA PROVINCE",
]


def get_institutional_prompt_snippet():
    """Returns a formatted string of the current Sinhala-to-English mappings for AI prompt injection."""
    snippet = "SRI LANKA POLICE INSTITUTIONAL TERMINOLOGY (Official Mappings):\n"
    # Select a relevant subset or full list depending on prompt size constraints
    # For now, let's include the full Sinhala_to_English mapping but limit counts to avoid bloat
    for sin, eng in list(SINHALA_TO_ENGLISH.items())[:300]: 
        snippet += f"- {sin} -> {eng}\n"
    return snippet


def enforce_terminology(text):
    """Enforce standard English station names via regex and phonetic alias mapping."""
    if not text: return text
    processed = text
    
    # 1. Handle common phonetic mismatches that AI often makes
    PHONETIC_ALIASE_MAP = {
        "Meegamuwa": "NEGOMBO",
        "Halawatha": "CHILAW",
        "Halawata": "CHILAW",
        "Mahanuwara": "KANDY",
        "Madakalapuwa": "BATTICALOA",
        "Yapanaya": "JAFFNA",
        "Trincomalee": "TRINCOMALEE", 
    }
    
    for phonetic, official in PHONETIC_ALIASE_MAP.items():
        pattern = re.compile(re.escape(phonetic), re.IGNORECASE)
        processed = pattern.sub(official, processed)

    # 2. Perform Case-Insensitive replacements for all standard English names in the map
    # We use word boundaries \b to avoid partial matches
    for sin, eng in SINHALA_TO_ENGLISH.items():
        if not eng or len(eng) < 3: continue
        pattern = re.compile(r'\b' + re.escape(eng) + r'\b', re.IGNORECASE)
        processed = pattern.sub(eng.upper(), processed)
        
    return processed


import difflib
import re

def get_station_info(station_name):
    """Look up station info, return dict or default."""
    if not station_name or str(station_name).lower() == "unknown":
        return {"province": "UNKNOWN DISTRICT", "dig": "UNKNOWN DIG", "div": "UNKNOWN Div."}

    info = STATION_MAP.get(station_name)
    if info:
        return info
        
    # Standardize input for fuzzy matching
    st_clean = re.sub(r'(?i)\b(?:Special Investigation Unit|North|South|East|West|Central|HQ|Post|Police|Station)\b', '', str(station_name))
    st_clean = re.sub(r'[,.\s]+', ' ', st_clean).strip()
        
    # Try exact substring match first (most reliable)
    for key in STATION_MAP:
        if key.lower() in str(station_name).lower() or str(station_name).lower() in key.lower():
            return STATION_MAP[key]
            
    # Try fuzzy match (resolves spelling errors like Ambalipitiya -> Embilipitiya / Ambalantota)
    if st_clean:
        # Increase n=3 to allow more candidates and check closely
        matches = difflib.get_close_matches(st_clean, STATION_MAP.keys(), n=3, cutoff=0.55)
        if matches:
            # Pick the best match but only if it's statistically significant
            return STATION_MAP[matches[0]]
            
    # Default Fallback (Institutional: Do not guess Western Province if unknown)
    return {"province": "UNKNOWN DISTRICT", "dig": f"DIG {station_name}", "div": f"{station_name} Div."}