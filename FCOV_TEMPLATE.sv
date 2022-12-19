covergroup cg_AAA;
	//  put options here if required
cp_rxpkt_len: coverpoint bm.pktpkt_en {
  at_least  = 10;
  bins      mornal[] = { { [65:1517] } };
  bins           max = { { 1518 } };
  bins      oversize = { { [1519:$] } };
} 
cp_port_en: coverpoint port_en {
  comment = to cover port enable;
  bins        all_on = { { 6'b111111 } };
} 
cp_speed: coverpoint speed iff(link) {
  bins          100M = { { 'b10 } };
  bins            1G = { { 'h2 } };
  bins          500M = { { 2'b11 } };
} 
cp_vlan_en: coverpoint vlan_en;
cp_spinore_ser_format: coverpoint {sc_reg_obj.spic_ctrlr0_scpol, sc_reg_obj.spic_ctrlr0_scph} {
  bins        mode_1 = { { 2'b01 } };
} 
cp_rxpkt_len_trans: coverpoint bm.pktpkt_en {
  bins       MAX_MIN = ( ( 1518 => 64 ) );
} 
cc_pktlen_port_en: cross pkt_len, port_en;
endgroup

covergroup cg_BBB;
	//  put options here if required
cp_chipmode: coverpoint  mode {
  bins         MODE1 = { { 2'b01 } };
  bins         MODE2 = { { 2'b10 } };
  illegal_bins        MODE3 = { { 2'b11 } };
} 
endgroup

