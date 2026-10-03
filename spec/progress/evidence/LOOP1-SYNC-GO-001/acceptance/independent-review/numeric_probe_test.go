package core
import("testing";"strings";"math/big";"math/rand";"math";"encoding/json";"fmt")
func TestIndependentNumericDifferential(t *testing.T){
r:=rand.New(rand.NewSource(734)); cap:=big.NewInt(math.MaxInt64)
for i:=0;i<8000;i++{ n:=1+r.Intn(60);d:=make([]byte,n);d[0]=byte('1'+r.Intn(9));for j:=1;j<n;j++{d[j]=byte('0'+r.Intn(10))};s:=string(d);if r.Intn(2)==0{at:=1+r.Intn(n);s=s[:at]+"."+s[at:]+"0"};s+=fmt.Sprintf("e%+d",r.Intn(150)-80);if r.Intn(4)==0{s="-"+s};q,ok:=new(big.Rat).SetString(s);if !ok{t.Fatal(s)};wantOK:=q.IsInt()&&q.Sign()>=0;var want int64;if wantOK{if q.Num().Cmp(cap)>0{want=math.MaxInt64}else{want=q.Num().Int64()}};out,e:=syncJSON(strings.NewReader("{\"afterSeq\":"+s+"}"));if e!=nil{t.Fatal(s,e)};var m map[string]json.RawMessage;if json.Unmarshal(out,&m)!=nil{t.Fatal(string(out))};got,valid:=syncInteger(m["afterSeq"],math.MaxInt64);if valid!=wantOK||(valid&&got!=want){t.Fatalf("input %s got %d/%v expected %d/%v",s,got,valid,want,wantOK)}}
}
