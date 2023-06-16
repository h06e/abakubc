def update_stress(stress):
    """
    calcul les contraintes macro
    see “calcul_contraintes_macro_KUBC.pdf” file
    """
    # calcul des pseudo contraintes (= contrainte x section, en N)
    # PseudoContrH  =  forces[‘F5’]  + forces[‘F6’]  + forces[‘F15’]  + forces[‘F16’]
    # PseudoContrV  =  forces[‘F3’]  + forces[‘F4’]  + forces[‘F7’]   + forces[‘F8’]
    # PseudoContrC1 =  forces[‘F5’]  + forces[‘F6’]  - forces[‘F1’]   - forces[‘F2’]
    # PseudoContrC2 =  forces[‘F7’]  + forces[‘F8’]  - forces[‘F13’]  - forces[‘F14’]
    PseudoContrH  =  1/2*(forces[‘F5’]  + forces[‘F6’]  + forces[‘F15’]  + forces[‘F16’])  + 1/2 * (forces[‘F1’]   +  forces[‘F2’]   +  forces[‘F9’]   +  forces[‘F10’])
    PseudoContrV  =  1/2*(forces[‘F3’]  + forces[‘F4’]  + forces[‘F7’]   + forces[‘F8’])   + 1/2 * (forces[‘F11’]  +  forces[‘F12’]  +  forces[‘F13’]  +  forces[‘F14’])
    PseudoContrC1 =  1/2*(forces[‘F5’]  + forces[‘F6’]  - forces[‘F1’]   - forces[‘F2’])   + 1/2 * (forces[‘F9’]   +  forces[‘F10’]  -  forces[‘F15’]  -  forces[‘F16’])
    PseudoContrC2 =  1/2*(forces[‘F7’]  + forces[‘F8’]  - forces[‘F13’]  - forces[‘F14’])  + 1/2 * (forces[‘F11’]  +  forces[‘F12’]  -  forces[‘F3’]   -  forces[‘F4’])
    PseudoContrC  =  0.5*(PseudoContrC1 + PseudoContrC2)
    # calcul des résidus d’effort (= écart au PFS)
    ResiduHb =  - forces[‘F9’]  - forces[‘F10’]  + forces[‘F15’] + forces[‘F16’]
    ResiduHh =    forces[‘F5’]  + forces[‘F6’]   - forces[‘F1’]  - forces[‘F2’]
    ResiduH  =   ResiduHb + ResiduHh
    ResiduVb =    forces[‘F11’] + forces[‘F12’]  + forces[‘F13’] + forces[‘F14’]
    ResiduVh =    forces[‘F7’]  + forces[‘F8’]   + forces[‘F3’]  + forces[‘F4’]
    ResiduV  =   -ResiduVb + ResiduVh
    ResiduMO =  0.308/2*(forces[‘F11’] + forces[‘F12’] - forces[‘F9’]  - forces[‘F10’]) # (0.3/2 = demie-largeur d’éprouvette)
    ResiduMB =  0.308/2*(forces[‘F15’] + forces[‘F16’] - forces[‘F13’] - forces[‘F14’]) # (0.3/2 = demie-largeur d’éprouvette)
    ResiduMC =  0.308/2*(forces[‘F7’]  + forces[‘F8’]  - forces[‘F5’]  - forces[‘F6’])  # (0.3/2 = demie-largeur d’éprouvette)
    ResiduMD =  0.308/2*(forces[‘F1’]  + forces[‘F2’]  - forces[‘F3’]  - forces[‘F4’])  # (0.3/2 = demie-largeur d’éprouvette)
    ResiduM  =  (ResiduMO + ResiduMB + ResiduMC + ResiduMD)
    # stress[0:PARAM._NB_FORCE_CAL] = [PseudoContrH, PseudoContrV, PseudoContrC, ResiduH, ResiduV, ResiduM]
    stress[‘S1’] = PseudoContrH/(288)
    stress[‘S2’] = PseudoContrV/(288)
    stress[‘S3’] = PseudoContrC/(288)
    stress[‘R1’] = ResiduH
    stress[‘R2’] = ResiduV
    stress[‘M3’] = ResiduM
           
# F1 = D_int_horiz  (17/235,103/235,189/235)
# F2 = D_ext_horiz  (17/235,103/235,189/235)
# F3 = D_ext_vert   (17/235,135/235,48/235)
# F4 = D_int_vert   (17/235,135/235,48/235)
# F5 = C_int_horiz  (220/235,106/235,35/235)
# F6 = C_ext_horiz  (220/235,106/235,35/235)
# F7 = C_int_vert   (219/235,188/235,55/235)
# F8 = C_ext_vert   (219/235,188/235,55/235)
# F9 = 0_ext_horiz  (2/235,37/235,80/235)
# F10 = 0_int_horiz (2/235,37/235,80/235)
# F11 = 0_ext_vert  (118/235,66/235,153/235)
# F12 = 0_int_vert  (118/235,66/235,153/235)
# F13 = B_ext_vert  (178/235,110/235,223/235)
# F14 = B_int_vert  (178/235,110/235,223/235)
# F15 = B_ext_horiz (198/235,40/235,23/235)
# F16 = B_int_horiz (198/235,40/235,23/235)