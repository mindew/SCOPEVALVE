
const int GSR=A1;
float sensorValue=0.;
float gsr_average=0.;

void setup(){
  Serial.begin(9600);
  
//  Serial.println("CLEARDATA"); //clears up any data left from previous projects
//
//  Serial.println("LABEL,Acolumn"); //always write LABEL, so excel knows the next things will be the names of the columns (instead of Acolumn you could write Time for instance)
//
//  Serial.println("RESETTIMER"); //resets timer to 0
}

void loop(){
  long sum=0;
  for(int i=0;i<10;i++)           //Average the 10 measurements to remove the glitch
      {
      sensorValue=analogRead(GSR);
      sum += sensorValue;
      delay(5);
      }
   gsr_average = sum/10.0;
   Serial.println(gsr_average);
}
