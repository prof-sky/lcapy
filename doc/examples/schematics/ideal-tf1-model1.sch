W1 5 3; right=1.5, f=i_1
W2 6 4; right=1.5
W3 1 7; right=1.5, f<=i_2
W4 2 8; right=1.5
P1 5 6; down=1.5, v=v_1
P2 7 8; down=1.5, v=v_2
F1 3 4 E1 F1; down=1.5, l=\frac{N_2}{N_1} i_2
E1 1 2 5 6 E1 0; down=1.5, a=\frac{N_2}{N_1} v_1
O 4 2; right
; draw_nodes=connections, label_nodes=none, style=american, voltage_dir=RP, label_style=value
