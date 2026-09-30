// Inspect every Go file, including build-tagged files, using the standard parser.
package main

import (
	"encoding/json"
	"go/ast"
	"go/parser"
	"go/token"
	"os"
	"path/filepath"
	"strconv"
)

type source struct {
	Path      string   `json:"path"`
	Package   string   `json:"package"`
	Imports   []string `json:"imports"`
	Functions []string `json:"functions"`
	Types     []string `json:"types"`
	Calls     []string `json:"calls"`
	Strings   []string `json:"strings"`
}

func name(e ast.Expr) string {
	switch n := e.(type) {
	case *ast.Ident:
		return n.Name
	case *ast.SelectorExpr:
		return name(n.X) + "." + n.Sel.Name
	case *ast.StarExpr:
		return name(n.X)
	}
	return ""
}

func main() {
	root := os.Args[1]
	files := []source{}
	err := filepath.WalkDir(root, func(path string, d os.DirEntry, err error) error {
		if err != nil {
			return err
		}
		if d.IsDir() {
			return nil
		}
		if filepath.Ext(path) != ".go" {
			return nil
		}
		f, err := parser.ParseFile(token.NewFileSet(), path, nil, parser.AllErrors)
		if err != nil {
			return err
		}
		rel, err := filepath.Rel(root, path)
		if err != nil {
			return err
		}
		s := source{Path: filepath.ToSlash(rel), Package: f.Name.Name}
		for _, i := range f.Imports {
			value, _ := strconv.Unquote(i.Path.Value)
			s.Imports = append(s.Imports, value)
		}
		ast.Inspect(f, func(n ast.Node) bool {
			switch x := n.(type) {
			case *ast.FuncDecl:
				s.Functions = append(s.Functions, x.Name.Name)
			case *ast.TypeSpec:
				s.Types = append(s.Types, x.Name.Name)
			case *ast.CallExpr:
				s.Calls = append(s.Calls, name(x.Fun))
			case *ast.BasicLit:
				if x.Kind == token.STRING {
					value, _ := strconv.Unquote(x.Value)
					s.Strings = append(s.Strings, value)
				}
			}
			return true
		})
		files = append(files, s)
		return nil
	})
	if err != nil {
		panic(err)
	}
	if err = json.NewEncoder(os.Stdout).Encode(files); err != nil {
		panic(err)
	}
}
