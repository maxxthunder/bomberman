-- US: password screen, enter BBBBBBBB, END: the decoder runs with fuzz_arm()'s callbacks in place
to_password() at(fuzz_arm) type_pw({0,0,0,0,0,0,0,0}) submit() wait(15000)  -- about 160 codes run per frame
