// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { SecretStorage } from "vscode";
import got from 'got';

// this method is called when your extension is activated
// your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	const secrets = context['secrets']; //SecretStorage-object


	console.log('Congratulations, your extension "pydex" is now active!');

	let disposable = vscode.commands.registerCommand('pydex.helloSelection', async () => {
		const activeEditor = vscode.window.activeTextEditor;
		if (!activeEditor) {
			return;
		}
		let userToken = undefined;

		userToken = secrets.get("pydex-token");
		console.log("Fetched token", userToken);
		//@ts-ignore
		if (userToken === undefined || userToken._value === null) {
			let verified = false;
			userToken = await vscode.window.showInputBox({ title: 'Enter your API token', password: true });
			// Verify user token
			if (userToken) {
				// TODO: implement actual verification
				verified = true;
			}
			if (userToken && verified) {
				secrets.store("pydex-token", userToken);
			}
		}

		// const input = vscode.commands.executeCommand("vscode.window.showInputBox", {}, {});
		console.log("User token: ", userToken);

		// The code you place here will be executed every time your command is executed
		// Display a message box to the user
		const document = activeEditor.document;
		const selection = activeEditor.selection;

		const url = 'https://httpbin.org/anything';
		const data = await got(url).json();

		console.log("From got", data);
		// Get the word within the selection
		const word = document.getText(selection);
		console.log("Selection", selection);
		console.log("Selected word", word);
		const reversed = word.split('').reverse().join('');

		activeEditor.edit(editBuilder => {
			console.log("Edit builder", editBuilder);
			editBuilder.replace(selection, reversed);
		});
	});


	context.subscriptions.push(disposable);
	// context.subscriptions.push(hover)
}

// this method is called when your extension is deactivated
export function deactivate() {
	console.log("deactivated");
}
