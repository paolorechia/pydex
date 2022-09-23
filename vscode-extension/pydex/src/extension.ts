import * as vscode from 'vscode';
import { SecretStorage } from "vscode";
import got from 'got';

const pydexDevUrl = "https://dev.codex.api.openimagegenius.com";
const pydexProdUrl = "https://codex.api.openimagegenius.com";


// const pydexUrl = pydexDevUrl;
const pydexUrl = pydexProdUrl;

interface PydexResponse {
	response: EditResponse;
}

interface EditResponse {
	text: string;
	index: number;
}

async function usePydex(secrets: SecretStorage, command: string) {
	const activeEditor = vscode.window.activeTextEditor;
	if (!activeEditor) {
		return;
	}
	let userToken = await secrets.get("pydex-token");

	console.log("Fetched token", userToken);
	if (!userToken) {
		let verified = false;
		userToken = await vscode.window.showInputBox({ title: 'Enter your API token', password: true });
		// Verify user token
		if (userToken) {
			// TODO: implement actual verification
			verified = true;
		}
		if (userToken && verified) {
			await secrets.store("pydex-token", userToken);
		}
	}

	console.log("User token: ", userToken);
	const document = activeEditor.document;
	const selection = activeEditor.selection;

	const text = document.getText(selection);

	const requestBody = JSON.stringify({
		data: text
	});
	const url = `${pydexUrl}/${command}`;

	console.log("Calling API", url, "with body: ", requestBody);

	let response: PydexResponse | undefined = undefined;
	try {
		response = await got(url, {
			method: "POST",
			headers: {
				// eslint-disable-next-line @typescript-eslint/naming-convention
				"Content-Type": "application/json",
				// eslint-disable-next-line @typescript-eslint/naming-convention
				"Authorization": userToken
			},
			body: requestBody
		}).json();
	} catch (e: any) {
		const apiStatusCode = `Error calling API: ${e.response.statusCode}`;
		if (e.response.statusCode === 401 || e.response.statusCode === 403) {
			console.log("Unauthorized, deleting provided token");
			await secrets.delete("pydex-token");
		}
		try {
			const errorMessage = JSON.parse(e.response.body).Message;
			console.error(errorMessage);
			vscode.window.showErrorMessage(errorMessage);
		} catch (error) {
			console.error("Error parsing error response", error);
			vscode.window.showErrorMessage(apiStatusCode);
		}
	}

	if (response) {
		console.log("From got", response);
		const editedText = response.response.text;

		activeEditor.edit(editBuilder => {
			console.log("Edit builder", editBuilder);
			editBuilder.replace(selection, editedText);
		});
	}


};

export function activate(context: vscode.ExtensionContext) {

	const secrets: SecretStorage = context.secrets;

	const commands = [
		["addDocstring", "add_docstring"],
		["addTypeHints", "add_type_hints"],
		["addUnitTest", "add_unit_test"],
		["fixSyntaxError", "fix_syntax_error"],
		["improveCodeQuality", "improve_code_quality"],
	];
	commands.forEach(tuple_ => {
		const [commandName, pydexCommand] = tuple_;
		const command = vscode.commands.registerCommand(`pydex.${commandName}`, () => {
			usePydex(secrets, pydexCommand);
		});
		context.subscriptions.push(command);
	});
}

// this method is called when your extension is deactivated
export function deactivate() {
	console.log("deactivated");
}
