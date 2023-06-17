import logging

import openai
import tiktoken
from shiny import App, reactive, render, ui

from logging_config_slacksystem import configure_logging

configure_logging("pronounsapp.log", "DEBUG")
logger = logging.getLogger(__name__)

GPT_MODEL: str = "gpt-3.5-turbo-16k"

tags = ui.tags

css = tags.style(
    "body { background-color: Black; color: White;} "
    ".control-label {color: White;}"
    ".shiny-text-output-verbatim {color: White;}"
    "h2 {text-align: center; width: 86%;}"
)

app_ui = ui.page_fluid(
    css,
    tags.body(
        ui.panel_title(
            title=ui.tags.h2(
                "Replace Pronouns",
                # {"text-align": "center", "border": "dashed"},
                # id="title",
            ),
            window_title="Replace pronouns in text",
        ),
        ui.layout_sidebar(
            # The left side will have the inputs for pronouns and names
            sidebar=ui.panel_sidebar(
                ui.input_text("pronoun_subjective", "Subjective", placeholder="they"),
                ui.input_text("pronoun_objective", "Objective", placeholder="them"),
                ui.input_text(
                    "pronoun_possessive_determiner",
                    "Possessive Determiner",
                    placeholder="their",
                ),
                ui.input_text(
                    "pronoun_possessive",
                    "Possessive",
                    placeholder="theirs",
                ),
                ui.input_text(
                    "pronoun_reflexive",
                    "Reflexive",
                    placeholder="themself",
                ),
                ui.input_text("new_char_name", label="Enter a name:"),
                ui.input_text("replace_char_name", label="Character to replace:"),
                width=3,
            ),
            main=ui.panel_main(
                # the right side has the text to replace, a button to
                # replace the text, and the output text when complete
                ui.input_text_area(
                    "replace_text",
                    label="Enter text to replace:",
                    autocomplete=None,
                    height="200px",
                ),
                ui.input_action_button("replace_button", "Replace Text"),
                tags.br(),
                tags.label("Output"),
                ui.output_ui(
                    "output_text",
                ),
                {"font-size": "2.5em"},
                width=7,
            ),
        ),
    ),
)


def server(input, output, session):
    logger.debug("Starting server")

    @output
    @render.text
    @reactive.event(input.replace_button)
    def output_text():
        # function runs automatically when replace button clicked
        pronoun_subjective: str = input.pronoun_subjective()
        pronoun_objective: str = input.pronoun_objective()
        pronoun_possessive_determiner: str = input.pronoun_possessive_determiner()
        pronoun_possessive: str = input.pronoun_possessive()
        pronoun_reflexive: str = input.pronoun_reflexive()
        old_char_name: str = input.replace_char_name()
        new_char_name: str = input.new_char_name()
        replace_text: str = input.replace_text()

        # get the token count of the input text
        enc = tiktoken.encoding_for_model(GPT_MODEL)
        tokens: int = len(enc.encode(replace_text))
        # the prompt is the instructions for the GPT engine,
        # plus the text to replace
        prompt = f"""
        In the following text, replace every instance of {old_char_name} with {new_char_name}.
        For each personal pronoun in the text, determine from context if its antecedent is {old_char_name} or not.
        If it is, replace it as the following:
            If the pronoun is subjectve, replace it with {pronoun_subjective}.
            If the pronoun is objective, replace it with {pronoun_objective}.
            If the pronoun is possessive determiner, replace it with {pronoun_possessive_determiner}.
            If the pronoun is possessive, replace it with {pronoun_possessive}.
            If the pronoun is reflexive, replace it with {pronoun_reflexive}.
        Do not replace any pronouns that do not have {old_char_name} as their antecedent.
        Return just the text with the replacements, do not add any additional comments or text.
        Make sure that anywhere there are newlines in the text, there are also newlines in the output.
        
        The text is as follows:
        ```
        {replace_text}
        ```
        """.replace(
            "        ", ""
        )

        completion = openai.ChatCompletion.create(
            model=GPT_MODEL,
            # send the prompt to the GPT chat engine as a user message
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5,
            # max tokens is twice the number of tokens in the input text
            # assuming the output text being approximately the same length
            # plus a buffer of 400 tokens for the prompt and variance
            max_tokens=tokens * 2 + 400,
        )
        response_html: str = completion.choices[0].message["content"]  # type: ignore
        # change newline characters to html line breaks
        response_html: str = response_html.replace("\n\n", "<br><br>")
        # enclose the response in a paragraph tag
        response_html = f"<p>{response_html}</p>"
        logger.debug(f"{response_html=}")
        return response_html


logger.info("Starting app")

app = App(ui=app_ui, server=server)
