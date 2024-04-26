The qualia_s3_analog clock is based off of the kds_analog clock and uses
the qualia_portal module for display and wifi access.

The qualia_protal module supports multiple display types. The display_type
value must be set when the portal is created. This value is read from the 
python envronment and is stored in the settings.toml file. This code 
was developed with the 2.1 inch capacitive touch display. 

Example settings.toml:

DISPLAY_TYPE = "round21"

