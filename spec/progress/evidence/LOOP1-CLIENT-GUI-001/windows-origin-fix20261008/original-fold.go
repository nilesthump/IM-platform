package main
import("fmt";"strings";"net/url")
func ascii(a,b string)bool{if len(a)!=len(b){return false};for i:=0;i<len(a);i++{x,y:=a[i],b[i];if x>='A'&&x<='Z'{x+='a'-'A'};if y>='A'&&y<='Z'{y+='a'-'A'};if x!=y{return false}};return true}
func main(){u,e:=url.Parse("http://K.local");if e!=nil{panic(e)};fmt.Printf("originHost=%s requestHost=k.local proposalEqualFold=%v originalASCIIFold=%v\n",u.Host,strings.EqualFold(u.Host,"k.local"),ascii(u.Host,"k.local"));if !strings.EqualFold(u.Host,"k.local")||ascii(u.Host,"k.local"){panic("counterexample did not reproduce")}}
