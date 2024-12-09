import Bacon

# run the model, give load=True to load the model from the pickle file
msb2k = Bacon.Bacon('MSB2K') 

msb2k.inspect_run()

# predict the age at depth=20
msb2k.predict_age(20)

# predict the accumulation rate at depth=40
msb2k.predict_acc_rate(40)

# dump the model into a pickle file
msb2k.dump()