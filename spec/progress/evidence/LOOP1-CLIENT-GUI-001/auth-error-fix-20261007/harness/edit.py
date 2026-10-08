from pathlib import Path
import subprocess
R=Path('H:/.codex/worktrees/g/IM-platform')
assert Path(subprocess.check_output(['git','rev-parse','--show-toplevel'],text=True).strip()).resolve()==R.resolve()
assert subprocess.check_output(['git','status','--porcelain'],text=True).strip()==''
for path,old,new in [
('clients/mobile/app/src/main/kotlin/im/platform/client/ui/Auth.kt','if(status==401)"Session expired" else code?:"Request failed"','if(status==401 && code=="AUTH_INVALID_CREDENTIALS")"Invalid username or password" else if(status==401)"Session expired" else code?:"Request failed"'),
('clients/desktop/src/application/ui/auth.ts','response.status===401?"Session expired":typeof code==="string"?code:"Request failed"','response.status===401&&code==="AUTH_INVALID_CREDENTIALS"?"Invalid username or password":response.status===401?"Session expired":typeof code==="string"?code:"Request failed"')]:
 p=Path(path);s=p.read_text(encoding='utf-8');assert s.count(old)==1;s=s.replace(old,new);p.write_text(s,encoding='utf-8',newline='\n')
p=Path('tests/clients/gui/auth.mjs');s=p.read_text(encoding='utf-8');needle='const workspace=new Workspace();';assert s.count(needle)==1
s=s.replace(needle,needle+'''
reply={status:401,data:{error:{code:"AUTH_INVALID_CREDENTIALS",message:"Server detail must not be echoed"},requestId:S}};
const anonymous=new Auth("https://localhost:8443");
await assert.rejects(anonymous.login("fixture-user","incorrect-fixture-input"),error=>error.kind==="Invalid username or password");
assert.equal(anonymous.session,null);assert.equal(credentials.size,0);
await workspace.login("https://localhost:8443","fixture-user","incorrect-fixture-input");
assert.equal(workspace.state.error,"Invalid username or password");assert.equal(workspace.state.session,null);assert.equal(workspace.state.offlineAccount,null);assert.equal(workspace.state.busy,false);assert.equal(credentials.size,0);
console.log("PASS canonical invalid credentials remain anonymous with safe login error; no false session expiry or stored credential");
''');p.write_text(s,encoding='utf-8',newline='\n')
p=Path('clients/mobile/app/src/androidTest/kotlin/im/platform/client/ui/GuiAuthenticatedInstrumentation.kt');s=p.read_text(encoding='utf-8')
s=s.replace('if(args.getString("phase")=="evidence-complete"){','if(args.getString("phase") in listOf("evidence-complete","auth-errors")){')
needle='.put("conversationSelected",s.selected.isNotEmpty()).put("width",b.width)';assert s.count(needle)==1
s=s.replace(needle,'.put("conversationSelected",s.selected.isNotEmpty()).put("sessionPresent",s.session!=null).put("offlineAccountPresent",s.offlineAccount!=null).put("secureCurrentPresent",Preferences(targetContext).read("https://localhost:8443/current")!=null).put("width",b.width)')
needle='if(phase=="evidence-complete"){';assert s.count(needle)==1
s=s.replace(needle,'''if(phase=="auth-errors"){
    fun invalid(name:String){
     fill("Username",args.getString("avery")!!);fill("Password","wrong-fixture-password");backKeyboard();reach("Sign in");click("Sign in");await("Invalid username or password")
     val s=actualViewModel().state.value;verify(s.session==null&&s.offlineAccount==null&&!s.busy&&s.connection=="offline"&&s.error=="Invalid username or password")
     verify(prefs.read("https://localhost:8443/current")==null);verify(find(actualRoot(),"Session expired. Sign in again.")==null);top();reach("Invalid username or password");capture(name)
    }
    invalid("cold-auth-invalid-14")
    login(args.getString("avery")!!);navigate("Settings");top();repeat(8){click("+")};reach("Comfort");click("Comfort");verify(actualViewModel().state.value.appearance==Appearance("cold",22,1.2f));settingsControl("Sign out");await("Open your workspace")
    invalid("cold-auth-invalid-22")
    login(args.getString("avery")!!);toggleTheme();verify(actualViewModel().state.value.appearance==Appearance("warm",22,1.2f));settingsControl("Sign out");await("Open your workspace")
    invalid("warm-auth-invalid-22")
    login(args.getString("avery")!!);val slot=checkNotNull(prefs.read("https://localhost:8443/current"));verify(prefs.read(slot)!=null)
    navigate("Settings");reach("Refresh session");capture("real-session-before-expiry");controlled("expiry");click("Refresh session");await("Session expired. Sign in again.")
    val expired=actualViewModel().state.value;verify(expired.session==null&&expired.offlineAccount==null&&!expired.busy&&expired.connection=="offline")
    verify(prefs.read("https://localhost:8443/current")==null&&prefs.read(slot)==null);top();reach("Session expired. Sign in again.");capture("real-session-expired-cleared")
    result.putString("expiredSecureSlotAbsent","PASS current and former owned session credential absent")
   }else '''+needle)
needle='click("Sign in");await("Session expired. Sign in again.");capture("auth-error")';assert s.count(needle)==1;s=s.replace(needle,'click("Sign in");await("Invalid username or password");capture("auth-error")')
p.write_text(s,encoding='utf-8',newline='\n')
print('PASS minimal two-platform canonical invalid-credentials mapping, focused meaningful controls and original LF retained')