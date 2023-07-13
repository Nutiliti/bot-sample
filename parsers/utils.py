class Parser:
    def __init__(self, pdf):
        self.pdf = pdf
        self.conditions = []
        self.page_num = None
        self.result_format = Result.TEXT
        self.date_format = None
        self.match_index = None
        self.delimiter = None
        self.get_page = False
        self.debug_mode = False
        self.debug_output_file = None
        self.extract_words_args = ()
        self.extract_words_kwargs = {}

    def page(self, page_num):
          """Narrows down the search to a particular page"""
          self.page_num = page_num
          return self

    def directly_after(self, phrase, phrase_index=0):
        """Narrows down the search to the word/value directly after a particular phrase

        Optional args:
          phrase_index: if the phrase shows up multiple times, this index variable can be
            used to specify which occurance of the phrase to use. Defaults to 0.
        """
        def check_after(word, word_index, words):
            start_index = after_phrase(words, phrase, phrase_index)[1]
            return word_index == start_index
        self.conditions.append(check_after)
        return self

    def is_dollars(self):
        """Narrows down the search to only include dollar amounts
        (for example: "$42.27", "$82", or "-$9.63")
        """
        def check_is_dollars(word, word_index, words):
            # regex to match a dollar amount
            return re.match("^-?\$?[\d,]+\.?\d*$", word["text"])
        self.conditions.append(check_is_dollars)
        if self.result_format == Result.TEXT:
            self.result_format = Result.DOLLARS
        else:
            raise ValueError(
                "More than one format was specified for the parsed text")
        return self


    def is_date(self, date_format):
        """Narrows down the search to only include dates in the specified format

        Args:
          date_format: string specifying the format of the date, using format codes from
            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes
        """
        def check_is_date(word, word_index, words):
            try:
                date_end_index = get_date_text(
                    words, word_index, date_format)[1]
                words[word_index]["num_linked_words"] = date_end_index - word_index
                return True
            except DateFormatError:
                return False
        self.conditions.append(check_is_date)
        if self.result_format == Result.TEXT:
            self.result_format = Result.DATE
            self.date_format = date_format
        else:
            raise ValueError(
                "More than one format was specified for the parsed text")
        return self

    def args(self, *args, **kwargs):
        """Any arguments passed into this function will be forwarded to the extract_words
        function (from the pdfplumber library) that generates the list of words from the pdf.
        This can be used to tweak how and in what order words are extracted from the pdf.

        It may be useful to call .args(use_text_flow=True) if you're not finding a phrase next to
        the value you're trying to parse.

        See the pdfplumber documentation for more info: https://github.com/jsvine/pdfplumber#the-pdfplumberpage-class
        """
        self.extract_words_args = args
        self.extract_words_kwargs = kwargs
        return self

    def is_date_range(self, date_format, delimiter="-"):
        """Narrows down the search to only include dates ranges in the specified format.
        An example of a date range is "03/01/2021 - 04/01/2021".

        Args:
          date_format: string specifying the format of the dates, using format codes from
            https://docs.python.org/3/library/datetime.html#strftime-and-strptime-format-codes .
          delimiter: the string that separates the dates in the date range. For example,
            in "5/01/2021 to 06/01/2021" the delimeter is "to". Defaults to "-".
            If the start and end date come immediately after each other in the extracted words list,
            you can set the delimiter to an empty string.
        """
        delimiter = delimiter.strip()

    def check_is_date_range(word, word_index, words):
        try:
            start_date_end_index = get_date_text(
                words, word_index, date_format)[1]
            if delimiter == "":
                delimiter_word_length = 0
            else:
                delimiter_word_length = len(delimiter.split(" "))
            end_date_start_index = start_date_end_index + delimiter_word_length + 1
            if end_date_start_index >= len(words):
                return False
            end_date_end_index = get_date_text(
                words, end_date_start_index, date_format)[1]
            words[word_index]["num_linked_words"] = end_date_end_index - word_index
            return True
        except DateFormatError:
            return False
        self.delimiter = delimiter
        self.conditions.append(check_is_date_range)
        if self.result_format == Result.TEXT:
            self.result_format = Result.DATE_RANGE
            self.date_format = date_format
        else:
            raise ValueError(
                "More than one format was specified for the parsed text")
        return self


    def create_new_results():
        results = {
            "pdfBalance": {"status": "missing"},
            "dueDate": {"status": "missing"},
            "billAvailableDate": {"status": "missing"},
            "autopayDate": {"status": "missing"},
            "billDateRange": {"status": "missing"},
            "lastMeterDate": {"status": "missing"},
            "nextMeterDate": {"status": "missing"},
            "usageAmount": {"status": "missing"},
            "yearsOnBill": {"status": "missing"},
        }
        return results