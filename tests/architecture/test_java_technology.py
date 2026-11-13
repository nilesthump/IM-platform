import hashlib
import importlib.util
from pathlib import Path
import shutil
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('java_controls',ROOT/'ci/check_java_technology.py')
checker=importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)

class JavaTechnologyControls(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        for name in ('spec/architecture/baseline.md','spec/architecture/frozen-architecture.md',checker.ADR,checker.APPROVAL):
            dest=self.root/name;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,dest)
    def put(self,name,text):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf8')
    def pom(self,artifact,group='org.springframework.boot',scope=''):
        self.put('backend/java/pom.xml','<project><dependencies><dependency><groupId>'+group+'</groupId><artifactId>'+artifact+'</artifactId>'+scope+'</dependency></dependencies></project>')
    def test_existing_placeholder_and_approved_stack(self):
        self.put('backend/java/InfraPlaceholder.java','class InfraPlaceholder {}')
        self.assertEqual([],checker.check(self.root))
        for coordinate in checker.policy(self.root)['dependencies']:
            group,artifact=coordinate.split(':');self.pom(artifact,group)
            self.assertEqual([],checker.check(self.root),coordinate)
        self.put('backend/java/core/Hash.java','import org.springframework.security.crypto.bcrypt.BCrypt;')
        self.assertEqual([],checker.check(self.root))
    def test_orm_security_framework_and_dynamic_coordinates_fail(self):
        for group,artifact in [('org.hibernate.orm','hibernate-core'),('org.springframework.boot','spring-boot-starter-security'),('${group}','postgresql')]:
            self.pom(artifact,group);self.assertTrue(checker.check(self.root))
    def test_security_crypto_only_bcrypt(self):
        for reference in ['org.springframework.security.web.FilterChainProxy','org.springframework.security.crypto.password.PasswordEncoder','org.springframework.security.config.annotation.web.builders.HttpSecurity','jakarta.persistence.Entity']:
            self.put('backend/java/core/Forbidden.java','import '+reference+';')
            self.assertTrue(checker.check(self.root),reference)
    def test_malformed_build_and_unsupported_dynamic_build_fail(self):
        self.put('backend/java/pom.xml','<project>');self.assertTrue(checker.check(self.root))
        (self.root/'backend/java/pom.xml').unlink()
        self.put('backend/java/build.gradle','dependencies {}');self.assertTrue(checker.check(self.root))
    def test_authority_tamper_fails(self):
        self.put(checker.APPROVAL,'replacement approval');self.assertTrue(checker.check(self.root))
    def test_unapproved_test_dependency_does_not_bypass(self):
        self.pom('hibernate-core','org.hibernate.orm','<scope>test</scope>');self.assertTrue(checker.check(self.root))
        self.pom('junit-jupiter','org.junit.jupiter','<scope>test</scope>');self.assertEqual([],checker.check(self.root))
        self.pom('junit-jupiter','org.junit.jupiter');self.assertTrue(checker.check(self.root))
    def test_missing_policy_fails(self):
        (self.root/'spec/architecture/frozen-architecture.md').unlink();self.assertTrue(checker.check(self.root))
    def test_wrong_root_and_foreign_namespaces_fail(self):
        dependency = '<dependency><groupId>org.hibernate.orm</groupId><artifactId>hibernate-core</artifactId></dependency>'
        documents = [
            '<not-a-pom/>',
            '<project xmlns="urn:unknown"><dependencies>'+dependency+'</dependencies></project>',
            '<project xmlns="http://maven.apache.org/POM/4.0.0"><dependencies xmlns="urn:unknown">'+dependency+'</dependencies></project>',
            '<project><foreign:dependencies xmlns:foreign="urn:unknown">'+dependency+'</foreign:dependencies></project>',
        ]
        for document in documents:
            self.put('backend/java/pom.xml',document)
            self.assertTrue(any('unsupported Maven root or namespace' in error for error in checker.check(self.root)),document)
    def test_standard_maven_namespaces_pass_and_still_check_dependencies(self):
        for prefix, declaration in [('', 'xmlns="http://maven.apache.org/POM/4.0.0"'), ('m:', 'xmlns:m="http://maven.apache.org/POM/4.0.0"')]:
            document = '<{p}project {ns}><{p}dependencies><{p}dependency><{p}groupId>org.postgresql</{p}groupId><{p}artifactId>postgresql</{p}artifactId></{p}dependency></{p}dependencies></{p}project>'.format(p=prefix,ns=declaration)
            self.put('backend/java/pom.xml',document)
            self.assertEqual([],checker.check(self.root))
            self.put('backend/java/pom.xml',document.replace('org.postgresql','org.hibernate.orm').replace('>postgresql<','>hibernate-core<'))
            self.assertTrue(checker.check(self.root))
if __name__=='__main__':unittest.main()
