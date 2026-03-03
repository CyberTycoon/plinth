"""Code injection using LibCST for safe AST modification."""

from pathlib import Path

import libcst as cst

from pedestal.exceptions import CodeInjectionError
from pedestal.logger import logger


class RegistryTransformer(cst.CSTTransformer):
    """Transforms registry.py to add new router imports and registrations."""

    def __init__(self, import_path: str, router_name: str):
        super().__init__()
        self.import_path = import_path
        self.router_name = router_name
        self.has_import = False
        self.has_registration = False

    def visit_ImportFrom(self, node: cst.ImportFrom) -> bool:
        """Check if import already exists."""
        if isinstance(node.module, cst.Attribute):
            module_name = f"{node.module.value.value}.{node.module.attr.value}"
        elif isinstance(node.module, cst.Name):
            module_name = node.module.value
        else:
            return True

        if self.import_path in module_name:
            self.has_import = True
        return True

    def visit_Assign(self, node: cst.Assign) -> bool:
        """Check if router is already in ROUTERS list."""
        for target in node.targets:
            if isinstance(target.target, cst.Name) and target.target.value == "ROUTERS":
                if isinstance(node.value, cst.List):
                    for element in node.value.elements:
                        if isinstance(element.value, cst.Name):
                            if element.value.value == self.router_name:
                                self.has_registration = True
        return True

    def leave_Module(
        self, original_node: cst.Module, updated_node: cst.Module
    ) -> cst.Module:
        """Add import statement if not present."""
        if self.has_import:
            return updated_node

        # Parse import statement
        import_stmt = cst.parse_statement(
            f"from {self.import_path} import {self.router_name}"
        )

        # Add to beginning of file (after any __future__ imports)
        new_body = [import_stmt] + list(updated_node.body)
        return updated_node.with_changes(body=new_body)

    def leave_Assign(
        self, original_node: cst.Assign, updated_node: cst.Assign
    ) -> cst.Assign:
        """Add router to ROUTERS list."""
        if self.has_registration:
            return updated_node

        for target in original_node.targets:
            if isinstance(target.target, cst.Name) and target.target.value == "ROUTERS":
                if isinstance(original_node.value, cst.List):
                    new_elements = list(original_node.value.elements)
                    new_elements.append(
                        cst.Element(
                            value=cst.Name(self.router_name),
                            comma=cst.Comma(),
                        )
                    )
                    return updated_node.with_changes(
                        value=original_node.value.with_changes(elements=new_elements)
                    )
        return updated_node


class CodeInjector:
    """Handles safe code injection into Python files."""

    @staticmethod
    def inject_router(
        registry_path: Path,
        import_path: str,
        router_name: str,
    ) -> None:
        """Inject a router into the registry file.

        Args:
            registry_path: Path to registry.py
            import_path: Python import path (e.g., "src.api.v1.auth")
            router_name: Name of the router variable (e.g., "auth_router")

        Raises:
            CodeInjectionError: If injection fails
        """
        if not registry_path.exists():
            raise CodeInjectionError(str(registry_path), "Registry file not found")

        try:
            source = registry_path.read_text(encoding="utf-8")
            module = cst.parse_module(source)

            transformer = RegistryTransformer(import_path, router_name)
            modified = module.visit(transformer)

            registry_path.write_text(modified.code, encoding="utf-8")
            logger.success(f"Injected {router_name} into registry")

        except Exception as e:
            raise CodeInjectionError(str(registry_path), str(e)) from e

    @staticmethod
    def add_import_to_file(
        file_path: Path,
        import_path: str,
        import_name: str,
    ) -> None:
        """Add an import statement to a file.

        Args:
            file_path: Path to Python file
            import_path: Module path to import from
            import_name: Name to import
        """
        if not file_path.exists():
            raise CodeInjectionError(str(file_path), "File not found")

        try:
            source = file_path.read_text(encoding="utf-8")
            module = cst.parse_module(source)

            # Check if import already exists
            import_stmt = f"from {import_path} import {import_name}"
            if import_stmt in source:
                logger.info(f"Import already exists: {import_stmt}")
                return

            # Add import at the beginning
            new_import = cst.parse_statement(import_stmt)
            new_body = [new_import] + list(module.body)
            modified = module.with_changes(body=new_body)

            file_path.write_text(modified.code, encoding="utf-8")
            logger.success(f"Added import: {import_stmt}")

        except Exception as e:
            raise CodeInjectionError(str(file_path), str(e)) from e

