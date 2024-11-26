class LangSymbols:
    def __init__(self, **kwargs: str):
        """
        Values to set:
        - volt -> which symbol is used for voltages usually V or U; default U
        - total -> which text is used for a total current usually tot or ges; default ges
        """
        self.volt = kwargs.get('volt', 'U')
        self.total = kwargs.get('total', 'ges')
