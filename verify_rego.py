def verify(rego):
    #formula taken from sgwiki
    checksum_letters = "ZABCDEGHJKLMPRSTUXY"
    prefix_mod = {"11": "SG", "2": "SBS", "9": "SMB"} #, "7": "TIB", "12": "PD", "16": "PC"}
    weights = [5, 4, 3, 2]
    if rego[-1] not in checksum_letters:
        return False, "invalid checksum letter"
    if len(rego) > 5:
        return False, "invalid rego length"
    if not rego[:-1].isdigit():
        return False, ""
    letter = rego[-1]
    checksum_mod = checksum_letters.index(letter)
    mod_sum = checksum_mod
    for i in range(len(rego) - 1):
        mod_sum += weights[-i-1] * int(rego[-i-2])
    mod_sum %= 19
    #print(mod_sum)
    if str(mod_sum) not in prefix_mod:
        return False
    else:
        return prefix_mod[str(mod_sum)] + rego
    
#print(verify("8022U"))
#print(verify("5537Z"))
#print(verify("6098S"))
#print(verify("2E"))
#print(verify("1Z"))
#print(verify("169L"))