"""Bounded Java technology checks; actual semantics/dependency graph require Review."""
import hashlib
import json
import re
import xml.etree.ElementTree as ET

ADR = 'spec/architecture/decisions/ADR-0014-java-technology.md'
APPROVAL = 'spec/progress/evidence/LOOP1-JAVA-ARCH-001/human-approval.txt'

def policy(root):
    manifest = (root/'spec/architecture/baseline.md').read_text(encoding='utf8')
    fields = dict(re.findall(r'^- ([a-z_0-9]+): `([^`]+)`\s*$', manifest, re.M))
    raw = (root/'spec/architecture/frozen-architecture.md').read_bytes()
    if fields.get('sha256') != hashlib.sha256(raw).hexdigest():
        raise ValueError('canonical hash mismatch')
    if fields.get('java_revision_adr') != ADR or fields.get('java_approval_source') != APPROVAL:
        raise ValueError('Java ADR/approval linkage missing')
    if fields.get('java_approval_sha256') != hashlib.sha256((root/APPROVAL).read_bytes()).hexdigest():
        raise ValueError('Human approval hash mismatch')
    if 'Human-approved' not in (root/ADR).read_text(encoding='utf8'):
        raise ValueError('Human-approved ADR missing')
    match = re.search(r'<!-- java-technology-policy -->\s*```json\s*(.*?)\s*```',raw.decode('utf8'),re.S)
    if not match:
        raise ValueError('Java canonical policy missing')
    value = json.loads(match.group(1))
    if (value.get('decision') != 'ADR-0014-java-technology' or value.get('bcrypt_only') is not True
            or value.get('orm') is not False or value.get('security_framework') is not False
            or value.get('jnats_phase') != 'LOOP1-JAVA-IM-001'
            or not isinstance(value.get('dependencies'),list)
            or not all(isinstance(x,str) and ':' in x for x in value['dependencies'])):
        raise ValueError('Java policy shape/bounds invalid')
    return value

def check(root):
    # Missing/malformed external authority is a verifier failure. Internal defects
    # propagate; no fallback policy or empty-success result.
    try:
        approved = policy(root)
    except (OSError, ValueError) as error:
        return ['JAVA-TECH authority unavailable: '+str(error)]
    errors=[]
    base=root/'backend/java'
    for path in base.rglob('*'):
        if not path.is_file():
            continue
        relative=path.relative_to(root).as_posix()
        if path.name in {'build.gradle','build.gradle.kts'}:
            errors.append('JAVA-TECH '+relative+': dynamic Gradle dependencies not verified by bounded Maven checker')
        if path.name == 'pom.xml':
            try:
                tree=ET.fromstring(path.read_text(encoding='utf8'))
            except (OSError,ET.ParseError) as error:
                errors.append('JAVA-TECH '+relative+': malformed Maven input: '+str(error));continue
            # Strip only Maven namespace; any other namespace remains unknown.
            for element in tree.iter():
                element.tag=element.tag.removeprefix('{http://maven.apache.org/POM/4.0.0}')
            for node in tree.iter():
                if node.tag not in {'dependency','parent'}:
                    continue
                group=node.findtext('groupId','').strip();artifact=node.findtext('artifactId','').strip()
                coordinate=group+':'+artifact
                allowed=coordinate in approved['dependencies']
                if node.tag=='parent':
                    allowed=coordinate=='org.springframework.boot:spring-boot-starter-parent'
                elif coordinate=='org.springframework.boot:spring-boot-dependencies':
                    allowed=node.findtext('type')=='pom' and node.findtext('scope')=='import'
                elif coordinate=='org.junit.jupiter:junit-jupiter':
                    allowed=node.findtext('scope')=='test'
                if not allowed:
                    errors.append('JAVA-TECH '+relative+': unapproved or unresolved coordinate '+coordinate)
        if path.suffix=='.java':
            text=path.read_text(encoding='utf8')
            # Explicit imports and qualified uses catch common prohibited APIs.
            # No claim to resolve reflection, aliases or arbitrary runtime graphs.
            if re.search(r'\b(?:org\.hibernate|jakarta\.persistence|javax\.persistence)\b',text):
                errors.append('JAVA-TECH '+relative+': ORM API not approved')
            for reference in re.findall(r'\borg\.springframework\.security(?:\.[\w*]+)+',text):
                if not reference.startswith('org.springframework.security.crypto.bcrypt.'):
                    errors.append('JAVA-TECH '+relative+': only BCrypt primitive approved: '+reference)
    return errors
