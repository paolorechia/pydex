// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { SecretStorage } from "vscode";
import got from 'got';
// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
const pydexUrl = "https://dev.codex.api.openimagegenius.com";

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

	// The code you place here will be executed every time your command is executed
	// Display a message box to the user
	const document = activeEditor.document;
	const selection = activeEditor.selection;

	const text = document.getText(selection);

	const requestBody = JSON.stringify({
		data: text
	});
	const url = `${pydexUrl}/${command}`;

	console.log("Calling API", url, "with body: ", requestBody);
	const response: PydexResponse = await got(url, {
		method: "POST",
		headers: {
			// eslint-disable-next-line @typescript-eslint/naming-convention
			"Content-Type": "application/json",
			// eslint-disable-next-line @typescript-eslint/naming-convention
			"Authorization": userToken
		},
		body: requestBody
	}).json();

	console.log("From got", response);
	const editedText = response.response.text;

	activeEditor.edit(editBuilder => {
		console.log("Edit builder", editBuilder);
		editBuilder.replace(selection, editedText);
	});

};

export function activate(context: vscode.ExtensionContext) {

	const secrets: SecretStorage = context.secrets;

	console.log('Congratulations, your extension "pydex" is now active!');

	let disposable = vscode.commands.registerCommand('pydex.addDocstring', function () {
		usePydex(secrets, "add_docstring");
	});

	context.subscriptions.push(disposable);
}

// this method is called when your extension is deactivated
export function deactivate() {
	console.log("deactivated");
}
